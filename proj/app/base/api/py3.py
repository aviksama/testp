from .main import resource_meta


class PreResource(object, metaclass=resource_meta):
    _allowed_methods = ['get', 'put', 'post', 'delete']

    def __init__(self, request, *args, **settings):
        self.request = request
        super(PreResource, self).__init__(*args, **settings)