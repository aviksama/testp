from proj.auth.validators import field_validator


class InputMixin(object):
    escaped_json = None
    fields_and_validators = None
    validated_input = None
    request = None
    
    def raw_data_validation(self, source=None):
        if not source:
            try:
                source = self.escaped_json['data']
                assert isinstance(source, dict)
            except (KeyError, AssertionError):
                return {"error": "e:27 error in validation input"}, 400

        data = dict()  # this dict will hold datatype validated data from var:`data_source`
        invalid_fields = {}
        for field, validator_name in self.get_fields_and_validators():
            vname_whether_mandatory = validator_name.rsplit('_', 1)
            if vname_whether_mandatory[-1] == 'mandatory':
                mandatory = True
                validator_name = vname_whether_mandatory[0]
            else:
                mandatory = False
            try:
                data[field] = field_validator.validate(validator_name, source[field])  # should result in
                # ValueError in case of wrong type of data
            except ValueError as e:
                invalid_fields[field] = e.args[0]
            except KeyError:
                if mandatory:
                    invalid_fields[field] = "%s is a mandatory field" % field
        if invalid_fields:
            return {"error": invalid_fields}, 400
        self.validated_input = data

    def get_fields_and_validators(self):
        return self.fields_and_validators.items()

