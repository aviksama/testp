from functools import wraps
try:
    import ujson as json
except ImportError:
    import json

from proj.app.utils.exceptions import InvalidAuthorization


class LoginRequired(object):
    """
    purpose: validate incoming api requests after user signup and before user account mapping
    i.e the api's which doesn't need account being mapped or acccount being active
    :param func:
    :param verify_2fa: if user required to be verified by 2fa
    :return:
    """
    def __init__(self, check_device=False, check_ip=False, is_admin=False):
        self.check_device = check_device
        self.check_ip = check_ip
        self.is_admin = is_admin

    def __call__(self, func):
        @wraps(func)
        def wrap(*args, **kwargs):
            # print('in decorator')
            request = args[0].request
            ip = request.client_addr if self.check_ip else None
            auth_key = request.headers.get('X-AUTH-TOKEN')
            if not auth_key:
                raise InvalidAuthorization("unauthorized")
            if self.check_device:
                device_key = request.headers.get('X-DEVICE-KEY')
                if not device_key:
                    raise InvalidAuthorization("unauthorized")
            else:
                device_key = None
            data = get_auth_data(auth_key, device_key=device_key, ip=ip, renew=RENEW_SESSION_ALWAYS)
            if not data:
                raise InvalidAuthorization("unauthorized")
            if self.is_admin is True and not data.get('user_data', {}).get('is_admin'):
                raise InvalidAuthorization("unauthorized")
            kwargs.update(data)
            return func(*args, **kwargs)
        return wrap
