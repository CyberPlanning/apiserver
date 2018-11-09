import graphene

from .resolver import resolve_custom, resolve_cyber, resolve_hack2g2

class Collection(graphene.Enum):
    CYBER = 1
    HACK2G2 = 2
    CUSTOM = 3

    @property
    def description(self):
        return "%s events" % self.name.lower()

    def resolve(self, db, **args):
        if self == Collection.CYBER:
            return resolve_cyber(db, **args)
        elif self == Collection.HACK2G2:
            return resolve_hack2g2(db, **args)
        elif self == Collection.CUSTOM:
            return resolve_custom(db, **args)
        else:
            return []