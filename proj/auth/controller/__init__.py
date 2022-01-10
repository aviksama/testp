from __future__ import unicode_literals
try:
    import ujson as json
except ImportError:
    import json


from bson.objectid import ObjectId

from proj.app.base.api.main import Resource


class LoginView(Resource):

    def get(self, *args, **kwargs):
        return {}
    
