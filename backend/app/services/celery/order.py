import socket

from app.extensions import redis
from app.extensions.ext_celery import flask_celery


@flask_celery.task
def task_add_together(a=0, b=0):
    """
    使用关键字参数only
    :param a:
    :param b:
    :return:
    """
    from app.main import flask_app
    with flask_app.app_context():
        host = socket.gethostname()
        l_data = dict(
            a=a,
            b=b,
            host=host,
        )
        redis.hmset('celery_check', l_data)
        data = redis.hgetall('celery_check')
        data = {k.decode('utf8'): v.decode('utf8') for k, v in data.items()}
        flask_app.logger.info('task_add_together, locals: %s, redis data: %s', l_data, data)
        return data
