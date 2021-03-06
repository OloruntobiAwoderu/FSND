import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'cofee-shop-udacity.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'



class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code





def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            "code": "authorization_header_is_missing",
            "description": "Expects Authorization Header"}, 401)
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            "code": "Header is invalid",
            "description": "Authorization header must contain Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({
            "code": "Header_Invalid",
            "description": "Token noot found"}, 401)
    elif len(parts) > 2:
        raise AuthError({
            "code": "Header is invalid",
            "description": "Authorixation header must be bearer token"}, 401)
    return parts[1]


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            "code": "Invalid claims",
            "description": "JWT doesnt contain Permissions"}, 401)
    if permission not in payload['permissions']:
        raise AuthError({
            "code": "You are Unauthorized",
            "description": "Permissions not found"}, 401)
    return True





def verify_decode_jwt(token):

    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    if "kid" not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    rsa_key = {}

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                "code": "Expired_token",
                "description": "Expired Token"}, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'Invalid claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 401)

    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 401)




def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
