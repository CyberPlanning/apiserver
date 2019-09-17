import graphene

from ..authorization import permissions

from .datetype import DateTime

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

    affiliations = graphene.List(graphene.String)

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

    @permissions('view', 'groups')
    def resolve_affiliations(self, info, **args):
        return self.affiliations
