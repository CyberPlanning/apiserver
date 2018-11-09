import graphene
import datetime
from graphql.language import ast


class DateTime(graphene.Scalar):
    """
    Un type Date reçu d'une requête GraphQL.

    Dans la requête, on s'attend à recevoir une date à l'un des formats
    suivants :
      * [year]-[month]-[day]
      * [year]-[month]-[day]T[hour]:[minute]:[second].[millisecond]
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