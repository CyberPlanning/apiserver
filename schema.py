import graphene
import datetime
from functools import wraps
from pymongo import MongoClient
from graphql.language import ast

import planning as planningData


# CLIENT = MongoClient("mongo", 27017)
CLIENT = MongoClient("localhost", 27017)


# Query

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
    planning = graphene.Field(Planning,
                              collection=graphene.String(required=True),
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

    def resolve_planning(self, info, **args):

        db = CLIENT.planning
        mongo_planning = planningData.resolve(db, **args)

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
