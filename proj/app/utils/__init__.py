import datetime
import re
import importlib
import binascii
import random
import base64
import hashlib
import os
import inspect
import hmac
try:
    import ujson as json
except ImportError:
    import json
import string
import uuid
from decimal import Decimal, setcontext, getcontext, ROUND_DOWN
try:
    # python3
    from urllib.parse import urlencode
    urlencode = urlencode
    bytes = bytes
    unicode = str
    StringType = (bytes, unicode)
except ImportError:
    # python2
    from urllib import urlencode
    urlencode = urlencode
    bytes = str
    unicode = unicode
    StringType = (bytes, unicode)

from gevent import time
from bson import ObjectId
from Crypto.Cipher import AES

from proj.app import settings

NoneType = type(None)


def get_uuid_with_timestamp():  # timestamp based uuid 43 characters
    """
    :return:  First 32 characters are hex of UUID , next 11 characters are the hex of timestamp
    """
    timestamp = int(round(time.time() * 1000))
    return uuid.uuid4().hex + str(hex(timestamp).lstrip("0x"))


def hasher(string):
    hashed = hashlib.blake2s(string.encode('utf-8') + settings.X_SECRET_KEY).hexdigest()  # X_SECRET_KEY is always bytes
    return hashed


def keygen(length=32, variable_case=False):  # variable length(upto 32 characters) option of variable casing
    assert(isinstance(length, int)), "e:12 key generator length must be integer"
    if variable_case is not True:
        assert(length <= 32), "e:13 key generator length cannot be more than 32"
    if not variable_case:
        return uuid.uuid4().hex[:length]
    return ''.join(random.choice(string.digits + string.ascii_letters)
                   for _ in range(length))


def create_placeholder_value(unique_length=32):
    return settings.X_VALUE_PLACEHOLDER + keygen()


class DictList(dict):
    """This is a Data Structure which helps to retain the value of previous key when the same key with another value is
    passed. It will generate a list for each key and the list follows order of insertion
    """
    def __setitem__(self, key, value):
        try:
            val = self.__getitem__(key)
            val.append(value)
            super(DictList, self).__setitem__(key, val)
        except KeyError:
            val = list()
            val.append(value)
            super(DictList, self).__setitem__(key, val)

    def __init__(self, iterable=None, **kwargs):
        super(DictList, self).__init__()
        if iterable:
            for item in iterable:
                try:
                    val = list()
                    val.append(item[1])
                    self.__setitem__(item[0], val)
                except KeyError as e:
                    raise KeyError(e)
        if kwargs:
            for k, v in kwargs.items():
                val = list()
                val.append(v)
                self.__setitem__(k, val)


def import_by_path(path, module=False, silent=False):
    """
    :param path: Full non-relative path of the object in dotted form
    :param module: set to True to import modules safely
    :param silent: setting this to `True` will not throw any import error
    :return:
    """
    """try:
        modulename, classname = path.rsplit('.', 1)
    except ValueError as e:
        if not silent:
            e.msg = "%s doesn't look like a module path" % path
            raise e
    else:
        mod = importlib.import_module(modulename)
        if module and isinstance(mod, ModuleType):
            return mod
        klass = None
        if hasattr(mod, classname):
            klass = getattr(mod, classname)
        if not set_globals:
            return klass
        return classname, klass"""
    try:
        if '.' in path and module is False:
            modulename, classname = path.rsplit('.', 1)
            mod = importlib.import_module(modulename)
            return getattr(mod, classname)
        else:
            mod = importlib.import_module(path)
            return mod
    except ModuleNotFoundError:
        try:
            modulename, classname, methodname = path.rsplit('.', 2)
            mod = importlib.import_module(modulename)
            return getattr(getattr(mod, classname), methodname)
        except (ModuleNotFoundError, AttributeError):
            if not silent:
                raise ValueError("%s doesn't look like a valid path" % path, )
    except (ValueError, AttributeError) as e:
        if not silent:
            e.args = "%s doesn't look like a valid path" % path,
            raise ValueError(*e.args)


def render_url_template(url_template, sub_vals):  # sub_vals = {'user_id': '123123123'}
    url = url_template
    for k, v in sub_vals.items():
        url = re.sub('{'+k+'}', v, url)
    return url


def decimal_string_precision(amount, decimal_precision=8, total_digits=19):
    context = getcontext()
    context.prec = total_digits
    context.rounding = ROUND_DOWN
    setcontext(context)
    amount_string = str(Decimal(amount).normalize())
    split_amount = amount_string.partition('.')
    fraction = split_amount[2][:decimal_precision]
    return ''.join(split_amount[:2]+(fraction,))


try:
    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId) or isinstance(o, datetime.datetime) or isinstance(o, Decimal):
                return str(o)
            if isinstance(o, uuid.UUID):
                return o.hex
            return json.JSONEncoder.default(self, o)
except AttributeError:
    import json as legacy_json

    class JSONEncoder(legacy_json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId) or isinstance(o, datetime.datetime) or isinstance(o, Decimal):
                return str(o)
            if isinstance(o, uuid.UUID):
                return o.hex
            return json.JSONEncoder.default(self, o)


def list_segmenter_util(array, slab_size=500):
    segregated_transactions = list()
    iterations = (len(array) // slab_size) + 1
    end_index = slab_size
    start_index = 0
    for i in range(iterations):
        segregated_transactions.append(array[start_index: end_index])
        start_index = end_index
        end_index += slab_size
    return segregated_transactions


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        try:
            key = key.encode('utf-8')
        except (AttributeError, UnicodeDecodeError):
             pass
        if len(key) == 32:
            self.key = key
        else:
            self.key = hashlib.blake2s(key).digest()

    def encrypt(self, raw, with_checksum=True):
        raw = self._pad(raw)
        iv = os.urandom(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = iv + cipher.encrypt(raw)
        if with_checksum is True:
            checksum = hashlib.blake2s(encrypted+self.key).digest()[:7]
            return base64.urlsafe_b64encode(encrypted+checksum)
        return base64.urlsafe_b64encode(encrypted)

    def decrypt(self, enc, with_checksum=True):
        encrypted = base64.urlsafe_b64decode(enc)
        if with_checksum is True:
            encrypted_with_checksum = encrypted
            checksum = encrypted_with_checksum[-7:]
            encrypted = encrypted_with_checksum[:-7]
            computed_checksum = hashlib.blake2s(encrypted+self.key).digest()[:7]
            if not computed_checksum == checksum:
                raise ValueError("checksum failed")
        iv = encrypted[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(encrypted[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def extract_parmeters(func):
    params = inspect.signature(func).parameters
    param_names = list(params.keys())
    defaults = [v.default for v in params.values() if v.default != inspect._empty]
    return param_names, defaults


def build_external_signature(data):
    if not isinstance(data, bytes):
        data = data.encode()
    digester = hmac.new(settings.SHARED_SALT, data, hashlib.blake2s)
    return digester.hexdigest()


def build_internal_hash(data):
    if not isinstance(data, bytes):
        data = data.encode()
    return hashlib.blake2s(data).hexdigest()


def arbitrary_length_hex(length):
    bytes_length, is_odd = divmod(length, 2)
    if is_odd:
        return binascii.hexlify(os.urandom(bytes_length+1))[:length].decode()
    else:
        return binascii.hexlify(os.urandom(bytes_length)).decode()


def find_biwise_constructs(number, maxnum=16):
    constructs = []
    while number > 0 and maxnum > 0:
        if number >= maxnum:
            constructs.append(maxnum)
            number = number - maxnum
            maxnum = int(maxnum / 2)
        else:
            maxnum = int(maxnum / 2)
    return constructs