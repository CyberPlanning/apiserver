import graphene
import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from graphql.language import ast

client = MongoClient()
planning = client.planning


class DateTime(graphene.Scalar):
    """
    Un type Date reçu d'une requête GraphQL.
    Dans la requête, on s'attend à recevoir une date à l'un des formats
    suivants :
        - [year]-[month]-[day]
        - [year]-[month]-[day]T[hour]:[minute]:[second].[millisecond]
    Suite au parsing, la date est retournée au format datetime.
    """

    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return DateTime.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return datetime.datetime.strptime(value,
                                              "%Y-%m-%dT%H:%M:%S.%f")


class Event(graphene.ObjectType):
    title = graphene.String()
    start_date = DateTime()
    end_date = DateTime()
    event_id = graphene.String()

    classrooms = graphene.List(graphene.String)
    teachers = graphene.List(graphene.String)
    groups = graphene.List(graphene.String)


class Planning(graphene.ObjectType):
    events = graphene.List(Event)


class Query(graphene.AbstractType):
    planning = graphene.Field(Planning,
                              from_date=graphene.Argument(DateTime,
                                                          required=True),
                              to_date=graphene.Argument(DateTime),
                              event_id=graphene.String(),
                              title=graphene.String(),
                              groups=graphene.List(graphene.String),
                              classrooms=graphene.List(graphene.String),
                              teachers=graphene.List(graphene.String),
                              limit=graphene.Argument(graphene.Int)
                              )

    def resolve_planning(self, args, context, info):
        start_date = args["from_date"]
        mongo_filter = {"start_date": {"$gte": start_date}}

        if 'to_date' in args:
            mongo_filter["end_date"] = {"$lte": args["to_date"]}
        else:
            # le jour suivant à 0h, 0min, 0s, 0ms
            mongo_filter["end_date"] = {"$lte": datetime.timedelta(
                days=1,
                hours=-start_date.hour,
                minutes=-start_date.minute,
                seconds=-start_date.second,
                microseconds=-start_date.microsecond
            ) + start_date}

        if 'event_id' in args:
            mongo_filter["event_id"] = args["event_id"]
        if 'title' in args:
            mongo_filter["title"] = {"$regex": args["title"]}
        if 'groups' in args:
            mongo_filter["groups"] = {"$in": [group for group in args["groups"]]}
        if 'classrooms' in args:
            mongo_filter["classrooms"] = {"$in": [classroom for classroom in args["classrooms"]]}
        if 'teachers' in args:
            mongo_filter["teachers"] = {"$in": [teacher for teacher in args["teachers"]]}

        cursor = planning.planning_cyber.find(mongo_filter)
        cursor.sort("start_date", ASCENDING)

        if 'limit' in args and args['limit'] > 0:
            mongo_planning = cursor.limit(args['limit'])
        else:
            mongo_planning = cursor

        return Planning(events=[
            Event(title=e['title'],
                  start_date=e['start_date'],
                  end_date=e['end_date'],
                  event_id=e['event_id'],
                  classrooms=e['classrooms'],
                  teachers=e['teachers'],
                  groups=e['groups'])
            for e in mongo_planning])
