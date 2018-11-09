import graphene

from .schema import Query

schema = graphene.Schema(query=Query)
