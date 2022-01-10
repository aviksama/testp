"""
This is the main routes file where we import other application routes
"""
import re
import glob

from proj.app.utils import import_by_path


files = glob.iglob('*/*/routes.py')


def get_routes():
    global files
    for var in files:
        try:
            routes = import_by_path(re.sub('/', '.', re.sub('.py', '', '%s/routes' % var)), silent=True)
            if not routes:
                continue
        except (TypeError, ImportError):
            continue
        for route in routes:
            yield route
