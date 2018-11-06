from functools import wraps

from .permissions import PERMISSIONS


def checkPermissionExist(fn):
    @wraps(fn)
    def decorator(namespace, name):
        if namespace not in PERMISSIONS:
            raise Exception(
                'Namespace %s not in available permissions' % namespace)

        if name not in PERMISSIONS[namespace]:
            raise Exception(
                'Permission name %s not in namespace %s' % (name, namespace))

        return fn(namespace, name)
    return decorator

@checkPermissionExist
def permissions(namespace, name):

    permsName = "%s:%s" % (namespace, name)
    permsAll = "%s:*" % namespace

    def wrapper(fn):
        @wraps(fn)
        def decorator(self, info, *args, **kwargs):
            context = info.context
            token = context.get('token', None)
            if token is None:
                return None

            perms = token.get('permission', None)
            if perms is None:
                return None

            if permsName in perms or permsAll in perms:
                # print('Perms %s for %s OK' % (perms, permsName))
                return fn(self, info, *args, **kwargs)
            else:
                # print('Perms %s for %s \033[31mDENY\033[0m' % (
                    # perms, permsName))
                return None
        return decorator
    return wrapper