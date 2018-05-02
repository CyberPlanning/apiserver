## Request error

+ AuthorisationError: No authorisation header
+ AuthorisationError: Prefix authorisation header error: No a Bearer
+ AuthorisationError: No token: Only 1 part, space separate
+ AuthorisationError: Too many element in token: more than 2 part, space separate

## JWT error

+ InvalidSignatureError: Invalid signature

+ DecodeError(InvalidTokenError): Cannot be decoded

+ InvalidTokenError: Error in token :
    + InvalidIssuedAtError: Issued at is in the future (iat key)
    + MissingRequiredClaimError(InvalidTokenError): missing reqired key
    + ExpiredSignatureError(InvalidTokenError): Expired
    + ImmatureSignatureError(InvalidTokenError): 'Not before' in the future (nbf key)
    + InvalidAlgorithmError(InvalidTokenError): Algo not recognized

## User Auth

+ Exception: User not found
+ Exception: Password not match
