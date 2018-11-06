import graphene
import datetime
from graphql.language import ast

from .mongo import getClient
from .planning import resolve
from .authorization import permissions


# Query
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


class Event(graphene.ObjectType):
    """
    Un `event` est un cours.

    Il est définit par :
      * un nom
      * une date de début et de fin
      * une liste de salles
      * une liste de professeurs
      * une liste des groups qui y participent
    """

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

    @permissions('view', 'id')
    def resolve_event_id(self, info, **args):
        return self.event_id

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
    """
    La `planning` est la liste des courses dont les caractéristiques correspondent à la requête
    effectuée.
    """

    events = graphene.List(Event)


class Query(graphene.ObjectType):
    """
    La requête permet de filtrer les cours que l'on veut obtenir en fonction de plusieurs
    paramètres:
      * une date de début et de fin dans laquelle doit se trouver le cours, la date de début est
      obligatoire. S'il n'y a pas de date de fin elle sera mise au jour suivant de la date de début.
      * une liste de groupe a qui les cours seront affiliés. Le groupe est nommé en fonction de
      l'année et du numéro de groupe, par exemple : le groupe 2 en 1er année aura '12' (Optionnel)
      * une liste des salles et une liste des professeurs (Optionnel)
      * une limite de nombre de cours à retourner (Optionnel)

    Exemple:
    ```
    query test {
        planning(collection: "planning_cyber", fromDate: "2018-04-30") {
            events {
                title
                classrooms
            }
        }
    }
    ```
    """
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
                              limit=graphene.Argument(graphene.Int),
                              description='Planning'
                              )

    def resolve_planning(self, info, **args):
        db = getClient().planning
        mongo_planning = resolve(db, **args)

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
