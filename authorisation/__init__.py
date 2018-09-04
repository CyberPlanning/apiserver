#!/usr/bin/python3
# coding: utf-8

from functools import wraps

from .jwtHandler import (
    AuthorisationError,
    createJwtDefaultPayload,
    jwtEncodeHandler,
    jwtDecodeHandler,
    requestHandler
)
from .permissions import (PERMISSIONS, checkPermissionExist)
from .error import (JWTError, AuthorisationError)


# Décorator for Schema

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

