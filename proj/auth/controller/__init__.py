try:
    import ujson as json
except ImportError:
    import json

from proj.app.base.api.main import Resource
from proj.app import settings


class LoginView(Resource):

    def get(self, *args, **kwargs):
        return {}
    
