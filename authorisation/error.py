#!/usr/bin/python3
# coding: utf-8


class AuthorisationError(Exception):
    def __init__(self, message, status_code=401):
        super().__init__(self, message)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return self.message


class JWTError(Exception):
    pass
