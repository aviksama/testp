from __future__ import unicode_literals
from datetime import datetime, timedelta
import hashlib

from proj.app import settings


class Credentials(object):
    CLIENT_TYPE = 1
    SERVER_TYPE = 2

    def __init__(self, passkey=None, auth_type=CLIENT_TYPE, salt=settings.X_SECRET_KEY):
        self.passkey = passkey
        self.salt = salt
        if not passkey:
            assert (auth_type in [self.CLIENT_TYPE, self.SERVER_TYPE])
            if auth_type == self.CLIENT_TYPE:
                self.timeformat = '%d(%a)%m(%B)%Y-%H%M'
            else:
                self.timeformat = '%H%M-%m(%B)%d(%a)%Y'
            self.auth_type = auth_type

    def digest(self, data=None):
        # if data is supplied it must
        passkey = self.passkey
        if not self.passkey:
            passkey = datetime.utcnow().strftime(self.timeformat)
        if not data:
            digest = hashlib.sha256(passkey.encode('utf-8') + self.salt).hexdigest()
        else:
            digest = hashlib.sha256(passkey.encode('utf-8') + self.salt + str(data).encode('utf-8')).hexdigest()
        return digest

    def is_valid_digest(self, digest, data=None, flexibility=1, time_unit='minutes'):
        assert isinstance(flexibility, int)
        if not self.passkey:
            hash_range = [x - flexibility for x in range(flexibility * 2 + 1)]
            if time_unit == 'minutes':
                hash_range.reverse()
                hash_range[:flexibility+1] = reversed(hash_range[:flexibility+1])
            elif time_unit == 'seconds':
                hash_range.reverse()
            else:
                raise TypeError('invalid time unit specified')
            for i in hash_range:
                span_dict = {time_unit: i}
                passkey = (datetime.utcnow() - timedelta(**span_dict)).strftime(self.timeformat)
                if not data:
                    new_digest = hashlib.sha256(passkey.encode('utf-8') + self.salt).hexdigest()
                else:
                    new_digest = hashlib.sha256(passkey.encode('utf-8') + self.salt + str(data).encode('utf-8')).\
                        hexdigest()
                if new_digest == digest:
                    return True
        else:
            # new_digest = hashlib.md5(str(self.passkey + salt).encode('utf-8')).hexdigest()
            if not data:
                new_digest = hashlib.sha256(self.passkey.encode('utf-8') + self.salt).hexdigest()
            else:
                new_digest = hashlib.sha256(self.passkey.encode('utf-8') + self.salt + str(data).encode('utf-8')).\
                    hexdigest()
            if new_digest == digest:
                return True
        return False
