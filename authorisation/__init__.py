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
            if('token' not in context or
                context['token'] is None or
                'permission' not in context['token'] or
                    context['token']['permission'] is None):
                return None

            perms = context['token']['permission']
            if permsName in perms or permsAll in perms:
                print('Perms %s for %s OK' % (perms, permsName))
                return fn(self, info, *args, **kwargs)
            else:
                print('Perms %s for %s \033[31mDENY\033[0m' % (
                    perms, permsName))
                return None
        return decorator
    return wrapper


def token_required(fn):
    @wraps(fn)
    def decorator(self, info, *args, **kwargs):
        # try:
        token = requestHandler(info.context['request'])
        info.context['token'] = token
        return fn(self, info, token, *args, **kwargs)

    return decorator
