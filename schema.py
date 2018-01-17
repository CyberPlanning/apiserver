import graphene
import datetime
import re
from pymongo import MongoClient, ASCENDING
from graphql.language import ast


CLIENT = MongoClient("mongo", 27017)


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


class Query(graphene.ObjectType):
    db = CLIENT.planning
    planning = graphene.Field(Planning,
                              from_date=graphene.Argument(DateTime,
                                                          required=True),
                              to_date=graphene.Argument(DateTime),
                              event_id=graphene.String(),
                              title=graphene.String(),
                              affiliation_groups=graphene.List(
                                  graphene.String),
                              classrooms=graphene.List(graphene.String),
                              teachers=graphene.List(graphene.String),
                              limit=graphene.Argument(graphene.Int)
                              )

    def resolve_planning(self, info, from_date,
                         to_date=None,
                         event_id=None,
                         title=None,
                         affiliation_groups=None,
                         classrooms=None,
                         teachers=None,
                         limit=0):
        mongo_filter = {"start_date": {"$gte": from_date}}

        if to_date:
            mongo_filter["end_date"] = {"$lte": to_date}
        else:
            # le jour suivant à 0h, 0min, 0s, 0ms
            mongo_filter["end_date"] = {"$lte": datetime.timedelta(
                days=1,
                hours=-from_date.hour,
                minutes=-from_date.minute,
                seconds=-from_date.second,
                microseconds=-from_date.microsecond
            ) + from_date}

        if event_id:
            mongo_filter["event_id"] = event_id
        if title:
            mongo_filter["title"] = re.compile(title)
        if affiliation_groups:
            mongo_filter["affiliation"] = {
                "$in": [
                    re.compile(group) for group in affiliation_groups
                ]
            }
        if classrooms:
            mongo_filter["classrooms"] = {
                "$in": [
                    re.compile(classroom) for classroom in classrooms
                ]
            }
        if teachers:
            mongo_filter["teachers"] = {
                "$in": [
                    re.compile(teacher) for teacher in teachers
                ]
            }

        cursor = Query.db.planning_cyber.find(mongo_filter)
        cursor.sort("start_date", ASCENDING)

        if limit > 0:
            mongo_planning = cursor.limit(limit)
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


schema = graphene.Schema(query=Query)
