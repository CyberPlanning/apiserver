import jwt
from flask import current_app

from datetime import timedelta, datetime


class JWTError(Exception):
    def __init__(self, message, status_code=401):
        super().__init__(self, message)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return "%d: %s" % (self.status_code, self.message)


def createJwtDefaultPayload():
    iat = datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA', timedelta(seconds=300))
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA', timedelta(seconds=0))
    return {'exp': exp, 'iat': iat, 'nbf': nbf}


def jwtEncodeHandler(payload=None):
    secret = current_app.config.get('JWT_SECRET_KEY')
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    required_claims = current_app.config.get('JWT_REQUIRED_CLAIMS', ['exp', 'iat', 'nbf'])

    if not payload:
        payload = createJwtDefaultPayload()
    missing_claims = list(set(required_claims) - set(payload.keys()))

    if missing_claims:
        raise RuntimeError('Payload is missing required claims: %s' % ', '.join(missing_claims))

    return jwt.encode(payload, secret, algorithm=algorithm).decode()


def jwtDecodeHandler(token):
    secret = current_app.config.get('JWT_SECRET_KEY')
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    leeway = current_app.config.get('JWT_LEEWAY', timedelta(seconds=10))

    verify_claims = current_app.config.get('JWT_VERIFY_CLAIMS', ['signature', 'exp', 'nbf', 'iat'])
    required_claims = current_app.config.get('JWT_REQUIRED_CLAIMS', ['exp', 'iat', 'nbf'])

    options = {
        'verify_' + claim: True
        for claim in verify_claims
    }

    options.update({
        'require_' + claim: True
        for claim in required_claims
    })

    return jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)


def requestHandler(request):
    print("[JWT] Handle request")
    auth_header_value = request.headers.get('Authorization', None)
    auth_header_prefix = current_app.config.get('JWT_AUTH_HEADER_PREFIX', 'Bearer')

    if not auth_header_value:
        raise JWTError('No JWT header: Authorization header token not found', 400)

    parts = auth_header_value.split()
    print("[JWT] token %s" % parts)

    if parts[0].lower() != auth_header_prefix.lower():
        raise JWTError('Invalid JWT header: Unsupported authorization type')
    elif len(parts) == 1:
        raise JWTError('Invalid JWT header: Token missing')
    elif len(parts) > 2:
        raise JWTError('Invalid JWT header: Token contains spaces')

    return jwtDecodeHandler(parts[1])


