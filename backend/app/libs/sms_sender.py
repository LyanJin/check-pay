from flask import current_app

from app.constants.auth_code import SMS_CODE_MESSAGE_FORMAT, SMS_CODE_MESSAGE_FORMAT_YC_CN, \
    SMS_CODE_MESSAGE_FORMAT_YC_EN
from app.enums.sms import SMSProvider


class SMSSender:
    default_provider = SMSProvider.YUNPIAN

    def __init__(self, number, code):
        self.number = number
        self.code = code

    def send_by_aws(self):
        from app.libs.aws.sms import SMSToolKit
        message = SMS_CODE_MESSAGE_FORMAT.format(self.code)
        rst = SMSToolKit().send_sms(self.number, message)
        current_app.logger.info('code sent, msg: %s, rst: %s', message, rst)

    def send_by_yunpian(self):
        from app.libs.yunpian.sms import SMSToolKit
        if self.number.startswith('+86'):
            message = SMS_CODE_MESSAGE_FORMAT_YC_CN.format(self.code)
        else:
            message = SMS_CODE_MESSAGE_FORMAT_YC_EN.format(self.code)
        rst = SMSToolKit().send_sms(self.number, message)
        current_app.logger.info('code sent, msg: %s, rst: %s', message, rst)

    @classmethod
    def send_sms(cls, number, code):
        sender = cls(number, code)
        if cls.default_provider == SMSProvider.YUNPIAN:
            sender.send_by_yunpian()
        else:
            sender.send_by_aws()


if __name__ == '__main__':
    import os
    os.environ['YP_API_CODE'] = ''
    from app.main import flask_app
    with flask_app.app_context():
        # SMSSender.send_sms('+8618975532069', '1234')
        SMSSender.send_sms('+639166660270', '4321')
