from app.extensions.ext_celery import flask_celery
from app.libs.sms_sender import SMSSender


@flask_celery.task
def async_send_auth_code(phone, code):
    """
    异步发送验证码
    :param phone:
    :param code:
    :return:
    """
    from app.main import flask_app
    with flask_app.app_context():
        flask_app.logger.info('async_send_auth_code, phone: %s, code: %s', phone, code)
        SMSSender.send_sms(phone, code)
