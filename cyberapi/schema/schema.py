import graphene

from ..mongo import getClient

from .collection import Collection
from .event import Event
from .datetype import DateTime


# Query

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
        planning(collection: CYBER, fromDate: "2018-04-30") {
            events {
                title
                classrooms
            }
        }
    }
    ```
    """
    planning = graphene.Field(Planning,
                              collection=Collection(required=True),
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

        collection = Collection.get(args['collection'])

        events = collection.resolve(db, **args)

        return Planning(events=events)

