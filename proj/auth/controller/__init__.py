try:
    import ujson as json
except ImportError:
    import json

from proj.app.base.api.main import Resource
from proj.app import settings
from proj.app.dbops import Location, Department, Category
from sqlalchemy import and_


class GetLocations(Resource):

    def get(self, *args, **kwargs):
        with settings.Session() as session:
            res = session.query(Location).with_entities(Location.id, Location.name)
            res = [{'id': r[0], 'name': r[1]} for r in res]
        return {'data': res}


class GetDepartments(Resource):
    def get(self, *args, **kwargs):
        try:
            location_id = int(kwargs['location_id'])
        except ValueError:
            return {'data': []}
        with settings.Session() as session:
            res = session.query(Department).filter(Department.location_id == location_id).with_entities(
                Department.id, Department.name)
            res = [{'id': r[0], 'name': r[1]} for r in res]
        return {'data': res}


class GetCategories(Resource):
    def get(self, *args, **kwargs):
        try:
            location_id = int(kwargs['location_id'])
            department_id = int(kwargs['department_id'])
        except ValueError:
            return {'data': []}
        with settings.Session() as session:
            res = session.query(Category).join(Department).filter(
                and_(Department.id == department_id, Department.location_id == location_id)
            ).with_entities(Category.id, Category.name)
            res = [{'id': r[0], 'name': r[1]} for r in res]
        return {'data': res}