from __future__ import unicode_literals
import re
import string
from datetime import date
from functools import partial
import base64
import binascii

from six import string_types
import six
from dateutil import parser

from proj.app.utils import hasher, bytes

def keygen_validator(key, length=32, hex_only=False):
    if not isinstance(key, string_types):
        raise ValueError("%s is not a valid string, wrong type" % key)
    if len(key) != length:
        raise ValueError('%s is not a valid string, wrong lenth' % key)
    valid = all(c in string.hexdigits for c in key) and key.islower() if hex_only else key.isalnum()
    if valid:
        return key
    raise ValueError('%s is not a valid string, wrong type' % key)


mongoid_validator = partial(keygen_validator, length=24, hex_only=True)


def password_validator(password, min_length=7, max_length=100, mandate_numeric=True, mandate_special=True,
                       mandate_lowercase=True, mandate_uppercase=True, decode_first=False):
    fail = False
    if not isinstance(password, string_types) or not password.isascii():
        raise ValueError("%s is not a valid password" % password)
    if decode_first is True:
        try:
            password = base64.b64decode(password).decode()
        except (TypeError, binascii.Error, UnicodeDecodeError):
            raise ValueError("malformed input")
    if re.search(r'\s', password):
        fail = True
    if not len(password) > min_length and len(password) < max_length:
        fail = True
    raw_string = r''
    if mandate_numeric:
        raw_string += r'(?=[^0-9]*[0-9])'
    if mandate_special:
        raw_string += r'(?=[^!@#$&*~^]*[!@#$&*~^])'
    if mandate_lowercase:
        raw_string += r'(?=[^a-z]*[a-z])'
    if mandate_uppercase:
        raw_string += r'(?=[^A-Z]*[A-Z])'
    if not re.search(r'^%s.*$' % raw_string, password):  #
        # alphanumeric or must have at least 1 special character along with
        fail = True
    if not fail:
        return hasher(str(password))
    else:
        raise ValueError("invalid input for the field type")


def username_validator(value, length_max=43, length_min=1, allow_whitespace=False, turn_lower=False):
    if not isinstance(value, string_types) or not value.isascii():
        raise ValueError("%s is not a valid string for the field type" % value)
    if not length_min <= len(value) <= length_max:
        raise ValueError("value should have length between %s and %s" % (length_min, length_max))
    try:
        if allow_whitespace:
            match = re.match('^[\w\d]+(?!\n)[\s]?[\w\d]+(?!\n)$', value)
        else:
            match = re.match('^[\w\d]+(?!\n)$', value)
    except TypeError:
        ValueError("%s is not a valid string for the field type" % value)
    else:
        if match and len(match.group()) == len(value):
            if turn_lower:
                return value.lower()
            return value
    raise ValueError("%s is not a valid string for the field type" % value)


def phone_validator(value, len_min=5, len_max=15, remove_hyphens=False, is_cc=False):
    try:
        assert (not value.startswith('-') or not value.endswith('-') or 'e' not in value or '.' not in value)
        match = re.match(r'^(?!-|\+-)\+?[-0-9]*(?<!-$)$', value)
        if not match:
            raise ValueError
        value = match.group()
        new_value = re.sub(r'-|\+', '', value)
        if remove_hyphens is True:
            value = new_value
        else:
            value = re.sub(r'\+', '', value, 1)
            value = re.sub(r'-+', '-', value)
        assert len_min <= len(new_value) <= len_max
        if is_cc is True:
            return '+' + value
        return value
    except (ValueError, TypeError, AssertionError, AttributeError):
        raise ValueError("%s doesn't look like a phone or country code" % value)


def like_uuid(value, length_max=43, length_min=1, title_case=False, allow_whitespace=False):
    if not isinstance(value, string_types):
        raise ValueError("%s is not a valid string for the field type" % value)
    if not length_min <= len(value) <= length_max:
        raise ValueError("value should have length between %s and %s" % (length_min, length_max))
    try:
        if allow_whitespace:
            match = re.match('^[\w\d]+(?!\n)[\s]?[\w\d]+(?!\n)$', value)
        else:
            match = re.match('^[\w\d]+(?!\n)$', value)
    except TypeError:
        ValueError("%s is not a valid string for the field type" % value)
    else:
        if match:
            if len(match.group()) == len(value):
                if title_case is False:
                    return value
                return value.title()
            raise ValueError("%s is not a valid string for the field type" % value)
        else:
            raise ValueError("%s is not a valid string for the field type" % value)


def arbitrary_string_validator(value, permitted_specials_chars='-/,.', length_min=5, length_max=96, anywhere=False,
                               permit_whitespace=True):
    if not isinstance(value, string_types):
        raise ValueError("%s is not a valid string for the field type" % value)
    value = re.sub('\s{2,}', ' ', value).strip()
    if not length_min <= len(value) <= length_max:
        raise ValueError("value should have length between %s and %s" % (length_min, length_max))
    permitted_specials_chars = re.escape(permitted_specials_chars)
    if permit_whitespace is True:
        permitted_specials_chars += '\s'
    if anywhere is True:
        reg = '^[\w\d%s]+(?!\n)$' % permitted_specials_chars
    else:
        reg = '^[\w\d]+[\w\d%s]+?[\w\d]+(?!\n)$' % permitted_specials_chars
    match = re.match(reg, value)
    if match:
        if len(match.group()) == len(value):
            return value
        raise ValueError("%s is not a valid string for the field type" % value)
    else:
        raise ValueError("%s is not a valid string for the field type" % value)


def regex_validator(value, regex='.*', strip=' ', title_case=False, pass_value_with_error=True):
    pseudo_value = "input" if pass_value_with_error is False else None
    if not isinstance(value, string_types):
        raise ValueError("%s is not a valid string for the field type" % pseudo_value or value)
    match = re.match(regex, value)
    if not match:
        raise ValueError("%s is not a valid string for the field type" % pseudo_value or value)
    value = match.group().strip(strip)
    if title_case is True:
        return value.title()
    return value


def list_of_aritrary_strings_validator(value, permitted_specials_chars='-/,.', length_min=5, length_max=96,
                                       anywhere=False, permit_whitespace=True):
    if not value or not isinstance(value, list):
        raise ValueError("%s is not a valid value for the field type" % value)
    validator = partial(arbitrary_string_validator, permitted_specials_chars=permitted_specials_chars, length_min=
                        length_min, length_max=length_max, anywhere=anywhere, permit_whitespace=permit_whitespace)
    return [validator(v) for v in value]


def email_validator(address):
    try:
        match = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", str(address))
    except TypeError:
        raise ValueError("%s is not a valid email" % address)
    if match:
        return match.group().lower()
    else:
        raise ValueError("%s is not a valid email" % address)


def domain_validator(domain):
    try:
        match = re.match(r"^(?=.{4,255}$)([a-zA-Z0-9][a-zA-Z0-9-]{,61}[a-zA-Z0-9]\.)+[a-zA-Z0-9]{2,5}$", str(domain))
    except TypeError:
        raise ValueError("%s is not a valid domain" % domain)
    if match:
        return match.group().lower()
    else:
        raise ValueError("%s is not a valid domain" % domain)


def numeric(value, is_float=False):
    try:
        new_val = float(value) if is_float is True else int(value)
        return new_val
    except (ValueError, TypeError):
        raise ValueError("%s is not a valid integer value" % value)


def validate_date(value):
    try:
        if not isinstance(value, type(date.today())):
            dt = parser.parse(value).date()
        else:
            return value
        return dt
    except ValueError:
        raise ValueError("%s is not a valid date" % value)


def validate_datetime(value):
    try:
        dt = parser.parse(value)
        return dt
    except ValueError:
        raise ValueError("%s is not a valid datetime" % value)


def validate_list_of_strings(value):
    if isinstance(value, list):
        return list(map(str, value))
    else:
        raise ValueError("%s is not a valid value" % value)


def validate_list_of_int(value):
    if isinstance(value, list):
        try:
            return list(map(int, value))
        except ValueError:
            raise ValueError("%s is not a valid value" % value)
    else:
        raise ValueError("%s is not a valid value" % value)


def validate_bool(value):
    if not isinstance(value, bool):
        raise ValueError("%s is not a valid boolean value" % value)
    return value


def validate_string_in_string_arrays(value, array_of_values, change_to=None):
    if isinstance(value, bytes):
        try:
            value = value.decode('ascii')
        except ValueError:
            raise ValueError("%s is not a valid value for the field type supported values are: %s" % (
                value, ', '.join(array_of_values)))
    else:
        value = str(value)
    if change_to:
        value = getattr(value, change_to)()
    if value not in array_of_values:
        raise ValueError("%s is not a valid value for the field type supported values are: %s" % (
            value, ', '.join(array_of_values)))
    return value


class RegisterValidator(object):  # Registers and map validators to their field_names
    if six.PY2:
        __slots__ = ['INSTANCES']
    INSTANCES = {}

    def register(self, name=None, func=None):
        class_instances = self.__class__.INSTANCES
        if name and name not in class_instances:
            class_instances[name] = func
        else:
            raise ValueError("validator name must be unique")

    @classmethod
    def validate(cls, name=None, data=None):
        if not name:
            return None
        if isinstance(name, list):
            values = tuple()
            for n in name:
                try:
                    if n not in cls.INSTANCES:
                        value = data
                    else:
                        value = cls.INSTANCES[n](data)
                    values += value,
                except ValueError as e:
                    values += e,
                    continue
            return values
        if name not in cls.INSTANCES:
            return data
        return cls.INSTANCES[name](data)
