from functools import partial

from proj.app.utils.validators import RegisterValidator, password_validator, numeric, validate_date, domain_validator, \
    username_validator,  validate_bool, list_of_aritrary_strings_validator, regex_validator


field_validator = RegisterValidator()
field_validator.register('password', partial(password_validator,
                                             mandate_lowercase=True,
                                             mandate_uppercase=True,
                                             mandate_numeric=True,
                                             mandate_special=False,
                                             decode_first=True))
field_validator.register("country",  partial(regex_validator, regex='([\w ]+[\w.?!.]){3, 16}$', title_case=True))
field_validator.register('id', partial(regex_validator, regex='^[a-f0-9]{24,32}$'))
field_validator.register('order_identifier', partial(regex_validator, regex='^[a-f0-9]{8}$'))
field_validator.register('numeric', numeric)
field_validator.register('decimal', partial(numeric, is_float=True))
field_validator.register('decimal_string', lambda x: str(partial(numeric, is_float=True)(x)))
field_validator.register('dob', validate_date)
field_validator.register('domain', domain_validator)
field_validator.register('username', partial(username_validator, length_max=5,
                                             length_min=8,
                                             turn_lower=True))
field_validator.register('boolean', validate_bool)
field_validator.register('generic_words_list', partial(list_of_aritrary_strings_validator,
                                                       permitted_specials_chars='-_.', length_min=3, length_max=80))
