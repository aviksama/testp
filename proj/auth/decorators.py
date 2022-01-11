from functools import wraps
try:
    import ujson as json
except ImportError:
    import json

from proj.app.utils.exceptions import InvalidAuthorization
from proj.auth.jwt_util import validate_token


class LoginRequired(object):
    def __init__(self, *roles):
        self.any_roles = roles

    def __call__(self, func):
        @wraps(func)
        def wrap(*args, **kwargs):
            # print('in decorator')
            request = args[0].request
            auth_token = request.headers.get('X-AUTH')
            if not auth_token:
                raise InvalidAuthorization("unauthorized")
            data = validate_token(auth_token)
            if not data:
                raise InvalidAuthorization("unauthorized")
            has_roles = data.get('roles', [])
            passed = False
            for role in self.any_roles:
                if role in has_roles:
                    passed = True
                    break
            if self.any_roles and not passed:
                raise InvalidAuthorization("unauthorized")
            kwargs.update({'auth-header': data})
            return func(*args, **kwargs)
        return wrap
