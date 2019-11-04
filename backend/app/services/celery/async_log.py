from logging.handlers import SocketHandler

from app.extensions.ext_celery import flask_celery
from app.libs.telegram_kit import TelegramKit


@flask_celery.task
def async_send_log_to_telegram(msg):
    """
    异步发送日志到telegram
    :param msg:
    :return:
    """
    # !!!!!!!! 绝对不要在这里使用 current_app.logger 打印任何日志，否则会出现循环调用
    print('async_send_log_to_telegram: ', msg)
    TelegramKit.send_server_alert_message(msg)


@flask_celery.task
def async_send_log_to_socket(host, port, msg):
    """
    异步发送日志到目标socket
    :param host:
    :param port:
    :param msg:
    :return:
    """
    # !!!!!!!! 绝对不要在这里使用 current_app.logger 打印任何日志，否则会出现循环调用
    print('async_send_log_to_socket: ', msg)
    handler = SocketHandler(host=host, port=port)
    handler.send(msg.encode('utf8'))

