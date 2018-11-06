#!/usr/bin/python3
# coding: utf-8

# from graphql import GraphQLError


class AuthorizationError(Exception):
    def __init__(self, message, status_code=401):
        super().__init__(self, message)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return self.message

    def toDict(self):
        return {
            'errors': [
                {
                    'message': self.message,
                    'code': self.status_code
                }
            ]
        }


class JWTError(Exception):
    pass
