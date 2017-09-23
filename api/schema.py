import graphene

from pymongo import MongoClient
from graphene_django.types import DjangoObjectType
import graphene

client = MongoClient()
planning = client.planning

class PlanningType(graphene.ObjectType):
    title = graphene.String()
    start_date = graphene.types.datetime.DateTime()
    end_date = graphene.types.datetime.DateTime()
    event_id = graphene.String()
    
    classrooms = graphene.List(graphene.String)
    teachers = graphene.List(graphene.String)
    groups = graphene.List(graphene.String)

class Query(graphene.AbstractType):
    all_plannings = graphene.List(PlanningType, first=graphene.Int())
    
    def resolve_all_plannings(self, args, context, info):
        print(args)

        cursor = planning.planning_cyber.find()
        if'first' in args:
            mongo_planning = cursor.limit(args['first'])
        else:
            mongo_planning = cursor

        return [PlanningType(title=e['title'], start_date=e['start_date']) for e in mongo_planning]

