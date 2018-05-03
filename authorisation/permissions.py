#!/usr/bin/python3
# coding: utf-8

from functools import wraps

PERMISSIONS = {
    "view": [
        "teachers",
        "date",
        "classrooms",
        "groups",
        "title",
    ],
    "user": [
        "create",
        "update",
        "remove",
        "permissions",
    ]
}


# Decorator
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
