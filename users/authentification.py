import hashlib
import bcrypt

import authorisation

from flask import current_app


class AuthError(Exception):
    def __init__(self):
        super().__init__("User or password not match")


def getUserFromLogin(db, login):
    cursor = db['users_cyber'].find({
        'username': login
    })
    if cursor.count() == 0:
        raise AuthError()

    return cursor.next()


def resolve(db, login, password):
    sha2 = hashlib.sha256()
    sha2.update(login.encode())
    idHash = sha2.hexdigest()

    print('Login', login)

    user = getUserFromLogin(db, login)

    if not bcrypt.checkpw(password.encode(), user['hash'].encode()):
        raise AuthError()

    payload = authorisation.createJwtDefaultPayload()
    payload.update({
        'permission': user['permissions'],
        # 'id': user['_id'],
        'login': user['username'],
    })

    return authorisation.jwtEncodeHandler(payload)
