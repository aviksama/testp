class GenericException(Exception) :
    """Custom Exception base class"""
    def __init__(self, message, user_msg=None, errors={}):
        Exception.__init__(self, message)
        self.message = message
        self.errors = errors
        self.user_msg = user_msg

    def __str__(self):
        return self.message + ". Errors: " + str(self.errors)


class FieldValidationError(GenericException): pass
class ValueException(GenericException): pass
class FieldNotAvailableError(GenericException): pass
class IntegrityError(GenericException): pass
class InsertionException(GenericException): pass
class AuthenticationError(GenericException): pass
class InvalidAuthorization(GenericException): pass
class HttpWrongResonse(GenericException): pass
