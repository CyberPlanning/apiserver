import hashlib
import bcrypt

import jwtHandler

from flask import current_app


def getUserFromLogin(db, login):
    cursor = db['users_cyber'].find({
        'username': login
    })
    if cursor.count() == 0:
        raise Exception('WIP user not found')

    return cursor.next()


def resolve(db, login, password):
    sha2 = hashlib.sha256()
    sha2.update(login.encode())
    idHash = sha2.hexdigest()

    print('Login', login)

    user = getUserFromLogin(db, login)

    if not bcrypt.checkpw(password.encode(), user['hash'].encode()):
        raise Exception("WIP password not match")

    payload = jwtHandler.createJwtDefaultPayload()
    payload.update({
        'permission': user['permissions'],
        # 'id': user['_id'],
        'login': user['username'],
    })

    return jwtHandler.jwtEncodeHandler(payload)