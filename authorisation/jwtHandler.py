import jwt
from flask import current_app

from datetime import timedelta, datetime

from .error import (AuthorisationError, JWTError)

# Constants

DEFAULT_REQUIRED_CLAIMS = ['exp', 'iat', 'nbf']
DEFAULT_ALGORITHM = 'HS256'


def createJwtDefaultPayload():
    iat = datetime.utcnow()
    exp = iat + \
        timedelta(seconds=current_app.config.get('JWT_EXPIRATION_DELTA', 300))
    nbf = iat + \
        timedelta(seconds=current_app.config.get('JWT_NOT_BEFORE_DELTA', 0))
    return {'exp': exp, 'iat': iat, 'nbf': nbf}


def jwtEncodeHandler(payload):
    if not payload:
        raise JWTError('Missing payload')

    secret = current_app.config.get('JWT_SECRET_KEY')
    algorithm = current_app.config.get('JWT_ALGORITHM', DEFAULT_ALGORITHM)
    required_claims = current_app.config.get(
        'JWT_REQUIRED_CLAIMS', DEFAULT_REQUIRED_CLAIMS)

    missing_claims = list(set(required_claims) - set(payload.keys()))
    if missing_claims:
        raise JWTError('Payload is missing required claims: %s' %
                       ', '.join(missing_claims))

    return jwt.encode(payload, secret, algorithm=algorithm).decode()


def jwtDecodeHandler(token):
    secret = current_app.config.get('JWT_SECRET_KEY')
    algorithm = current_app.config.get('JWT_ALGORITHM', DEFAULT_ALGORITHM)
    leeway = timedelta(seconds=current_app.config.get('JWT_LEEWAY', 10))

    verify_claims = current_app.config.get(
        'JWT_VERIFY_CLAIMS', ['signature'] + DEFAULT_REQUIRED_CLAIMS)
    required_claims = current_app.config.get(
        'JWT_REQUIRED_CLAIMS', DEFAULT_REQUIRED_CLAIMS)

    options = {
        'verify_' + claim: True
        for claim in verify_claims
    }

    options.update({
        'require_' + claim: True
        for claim in required_claims
    })

    try:
        return jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)
    except jwt.InvalidSignatureError as e1:
        raise AuthorisationError(str(e1))
    except jwt.DecodeError as e2:
        raise AuthorisationError("Unable to decode token.")
    except jwt.InvalidTokenError as e3:
        raise AuthorisationError(str(e3))


def requestHandler(request):
    auth_header_value = request.headers.get('Authorization', None)
    auth_header_prefix = current_app.config.get(
        'JWT_AUTH_HEADER_PREFIX', 'Bearer')

    if not auth_header_value:
        raise AuthorisationError(
            'No JWT header: Authorization header token not found', 400)

    parts = auth_header_value.split()

    if parts[0].lower() != auth_header_prefix.lower():
        raise AuthorisationError(
            'Invalid JWT header: Unsupported authorization type')
    elif len(parts) == 1:
        raise AuthorisationError('Invalid JWT header: Token missing')
    elif len(parts) > 2:
        raise AuthorisationError('Invalid JWT header: Token contains spaces')

    return jwtDecodeHandler(parts[1])
