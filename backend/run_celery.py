import sys

from app.extensions.ext_celery import flask_celery
from app.main import flask_app

if __name__ == '__main__':
    # python run_celery.py -A app.main:flask_celery worker
    with flask_app.app_context():
        argv = sys.argv
        if len(argv) == 1:
            argv += '-A app.main:flask_celery worker'.split(' ')
        flask_celery.start(argv)
