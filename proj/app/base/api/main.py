import six
import re
import glob
try:
    import ujson as json
except ImportError:
    import json

import pyramid.httpexceptions as exc
from pyramid.view import view_config
from pyramid.response import Response

from proj.app.utils import DictList
from proj.app.utils import import_by_path


setattr(json, 'old_dumps', getattr(json, 'dumps'))
setattr(json, 'dumps', lambda *a, **kw: json.old_dumps(a[0]))


def monkey_patch_response(name, target):
    from webob import response
    setattr(response, name, target)


monkey_patch_response('json', json)

try:
    from html import escape
except ImportError:
    from cgi import escape


__all__ = ['Resource']


try:
    UnicodeType = unicode
except NameError:
    UnicodeType = str


class AdditionalContext(object):
    context = None
    funcs = None

    @classmethod
    def static_register(cls, func):
        data = func()
        if not isinstance(data, dict):
            return
        if not cls.context:
            cls.context = data
        else:
            cls.context.update(data)

    @classmethod
    def dynamic_register(cls, func):
        funcs = cls.funcs or []
        funcs.append(func)
        cls.funcs = funcs
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)
        return wrap

    @classmethod
    def get_context(cls, *args, **kwargs):
        if not cls.context:
            cls.context = {}
        if cls.funcs:
            for func in cls.funcs:
                data = func(*args, **kwargs)
                if isinstance(data, dict):
                    cls.context.update(data)


class resource_meta(type):

    def __new__(Klass, name, parent, attrs):
        if 'route_name' not in attrs:
            route_name = name.lower()
            attrs['route_name'] = route_name
        else:
            route_name = str(attrs['route_name'])
        New_Klass = type.__new__(Klass, name, parent, attrs)
        # todo: create a check for existing route before decorating classes
        # it will avoid errors due to unregistered route
        if New_Klass.__name__ in ('Resource', 'PreResource'):
            return New_Klass
        return view_config(route_name=route_name)(New_Klass)


if six.PY3:
    from .py3 import PreResource

else:
    class PreResource(object):
        __metaclass__ = resource_meta
        _allowed_methods = ['get', 'put', 'post', 'delete']

        def __init__(self, request, *args, **settings):
            self.request = request
            super(PreResource, self).__init__(*args, **settings)


class Resource(PreResource):
    delete_cookies = None
    set_cookies = None
    cookie_max_age = None
    _vars = None

    def __call__(self, *args, **kwargs):
        if self.request:
            meth = self.request.method.lower()
            if hasattr(self, meth) and meth in self._allowed_methods:
                # We are keeping `args` for future compatibility reasons
                kwargs.update(self.escaped_params)
                # return view_config(request_method=meth)(getattr(self, meth)(*args, **kwargs))
                return self._get_response(meth, *args, **kwargs)
            return Response(status=405)

    def _get_response(self, method, *args, **kwargs):
        retval = getattr(self, method)(*args, **kwargs)
        if self._vars and isinstance(self._vars, tuple):
            args = self._vars[0]
            kwargs = self._vars[1]
        if isinstance(retval, Response):
            return retval
        if isinstance(retval, tuple):
            context, status = retval
            if status == 404:
                return exc.HTTPNotFound()
        else:
            context = retval
            status = 200
        kwargs.update({'request': self.request, 'response': {'context': context, 'status': status}})
        AdditionalContext.get_context(*args, **kwargs)
        context.update(AdditionalContext.context)
        response = Response(json=context, status=status)
        response.md5_etag()
        response.cache_expires(60)
        headers = self.set_headers()
        if headers and isinstance(headers, dict):
            response.headers.update(headers)
        return view_config(request_method=method)(response)

    def set_headers(self):
        return

    @property
    def escaped_qs(self):
        """
        :return: this gives all the url parameters from query string
        """
        req_params = self.request.params
        keys = []
        esc_params = DictList()
        if req_params is not None:
            for d in req_params.dicts:
                keys.extend(d.mixed())
            for key in keys:
                value_list = req_params.getall(key)
                for value in value_list:
                    if issubclass(type(value), UnicodeType):
                        esc_value = escape(value)
                    else:
                        esc_value = value
                    esc_params.__setitem__(key, esc_value)
        return esc_params

    @property
    def escaped_url(self):
        if issubclass(type(self.request.url), UnicodeType):
            esc_value = escape(self.request.url)
        else:
            esc_value = self.request.url
        return esc_value

    @property
    def escaped_params(self):
        req_route_match = {}
        path_match = self.request.matchdict
        for key in path_match.keys():
            if issubclass(type(self.request.url), UnicodeType):
                req_route_match[key] = escape(path_match[key])
            else:
                req_route_match[key] = path_match[key]
        return req_route_match

    @property
    def escaped_json(self):
        try:
            # fields with empty values are discarded
            req_json = json.loads(escape(json.dumps(self.request.json), quote=False))
            if not isinstance(req_json, dict):
                raise ValueError()
            return req_json
        except (ValueError, TypeError):
            message = "couldn't find valid json object"
            raise ValueError(message)

    @property
    def input_file(self):
        req_file = self.request.POST['input_file'].file
        req_filename = escape(self.request.POST['input_file'].filename)
        return req_file, req_filename


# @important only import the classes defined in routes

# ### Auto Imports ########
files = glob.glob('*/*/controller/*.py')


def imports():
    for filename in files:
        try:
            class_dict_items = \
                {k: v for k, v in import_by_path(re.sub('/', '.', re.sub('.py', '', filename)), module=True).
                    __dict__.items() if not k.startswith('_')}
            print(re.sub('/', '.', re.sub('.py', '', filename)))
            for k, v in class_dict_items.items():
                globals()[k] = v
        except AttributeError:
            continue
imports()
# print globals()
###### end Auto Imports #######

