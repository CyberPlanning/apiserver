from datetime import timedelta, datetime

from ..authorization import createJwtDefaultPayload, jwtEncodeHandler

def generate_token(name, duration: "seconds", permissions=[]):
    iat = datetime.utcnow()
    nbf = iat
    exp = iat + timedelta(seconds=duration)

    payload = {
        'exp': exp,
        'iat': iat, 
        'nbf': nbf,
        'permission': permissions,
        'login': name,
    }

    return jwtEncodeHandler(payload)