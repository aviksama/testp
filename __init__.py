from gevent import monkey
monkey.patch_all()
import gevent
from gevent.pywsgi import WSGIServer
from pyramid.config import Configurator
from wsgicors import CORS

from proj.app.all_routes import get_routes


def main():
    config = Configurator()

    routes = get_routes()
    for route in routes:
        config.add_route(*route)
    config.scan('proj.app.base.api.main')
    config.scan('proj.app.exc')
    # app = config.make_wsgi_app()
    return CORS(config.make_wsgi_app(), headers="*", methods="*", origin="*")


if __name__ == '__main__':
    import sys
    try:
        port = int(sys.argv[1])
    except (IndexError, TypeError):
        port = 8443
    server = WSGIServer('0.0.0.0:%s' % port, main(),)
    print("starting server...")
    server = gevent.spawn(server.serve_forever)
    print('press ctrl+c to quit')
    gevent.joinall([server])