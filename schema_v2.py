import graphene
import datetime
from functools import wraps
from graphql.language import ast
from flask import current_app

from mongo import getClient
import planning as planningResolver

from authorisation import (requestHandler, token_required, permissions)
import users


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

    @permissions('view', 'title')
    def resolve_title(self, info, **args):
        return self.title

    @permissions('view', 'date')
    def resolve_start_date(self, info, **args):
        return self.start_date

    @permissions('view', 'date')
    def resolve_end_date(self, info, **args):
        return self.end_date

    @permissions('view', 'classrooms')
    def resolve_classrooms(self, info, **args):
        return self.classrooms

    @permissions('view', 'teachers')
    def resolve_teachers(self, info, **args):
        return self.teachers

    @permissions('view', 'groups')
    def resolve_groups(self, info, **args):
        return self.groups


class Planning(graphene.ObjectType):
    events = graphene.List(Event)


class Token(graphene.ObjectType):
    token = graphene.String()


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
                              limit=graphene.Argument(graphene.Int))

    auth = graphene.Field(Token,
                          login=graphene.String(required=True),
                          password=graphene.String(required=True))

    @token_required
    def resolve_planning(self, info, token, **args):

        print("\033[032mPlanning: \033[0m", info.context)

        db = getClient().planning
        mongo_planning = planningResolver.resolve(db, **args)

        return Planning(events=[
            Event(title=e['title'],
                  start_date=e['start_date'],
                  end_date=e['end_date'],
                  event_id=e['event_id'],
                  classrooms=e['classrooms'],
                  teachers=e['teachers'],
                  groups=e['groups'])
            for e in mongo_planning])

    def resolve_auth(self, info, **args):
        print("\033[032mAuth: \033[0m", info.context)

        db = getClient().planning
        token = users.resolve(db, **args)

        return Token(token)


# Mutations
class User(graphene.ObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    permissions = graphene.List(graphene.String)


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        permissions = graphene.List(graphene.String)

    ok = graphene.Boolean()
    user = graphene.Field(User)

    @staticmethod
    @token_required
    @permissions('user', 'create')
    def mutate(self, info, token, username, password, permissions):
        print('User', token)
        user = User(username=username, password=password,
                    permissions=permissions)

        # Create entry in db

        ok = True
        return CreateUser(user=user, ok=ok)


class Mutation(graphene.ObjectType):

    createUser = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
