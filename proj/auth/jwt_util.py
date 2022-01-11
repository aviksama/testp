import binascii
from jwt.jwk import jwk_from_pem
from jwt import JWT
from jwt.exceptions import JWTDecodeError
import time

from proj.auth.certs import private_key_pem, public_key_pem

rsa_jwk_priv = jwk_from_pem(private_key_pem, options={'alg': "RS256", 'typ': 'JWT', 'kid': 'Auth101', 'use': 'sign'})
rsa_jwk_pub = jwk_from_pem(public_key_pem, options={'alg': "RS256", 'typ': 'JWT', 'kid': 'Auth101', 'use': 'verify'})


jwt = JWT()


def create_token(name, *roles):
    iat = int(time.time())
    expires_at = iat + 3600
    jwtoken = jwt.encode(
        {"iss": "self", "sub": "auth issuance", "aud": "unknown", "exp": expires_at, "name": name, "iat": iat,
         "roles": list(roles)}, key=rsa_jwk_priv, alg=rsa_jwk_priv.options['alg'],
        optional_headers={"alg": "RS256", "typ": "JWT", "kid": 'Auth101'})
    return jwtoken


def validate_token(jwtoken):
    try:
        return jwt.decode(jwtoken, rsa_jwk_pub, do_verify=True, do_time_check=True)
    except (JWTDecodeError, binascii.Error):
        return {}
