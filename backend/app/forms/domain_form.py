from flask import current_app, request
from flask_restplus import ValidationError
from wtforms import StringField

from app.forms.base_form import BaseForm, stop_validate_if_error_occurred
from config import MerchantDomainConfig, MerchantEnum


class DomainForm(BaseForm):
    # 把域名取出来，当作表单字段使用
    domain = StringField(description="域名")
    merchant = StringField(description="商户名称")

    @classmethod
    def load_request_data(cls):
        data = super(DomainForm, cls).load_request_data()
        # 取出域名
        data['domain'] = request.host.split(':')[0]
        return data

    @stop_validate_if_error_occurred
    def validate_domain(self, domain):
        """
        从缓存中获取domain对应的商户名称，获取不到认为是非法的域名，则禁止访问
        :param domain:
        :return:
        """
        # current_app.logger.info('request domain: %s', domain.data)

        merchant = MerchantDomainConfig.get_merchant(domain.data)
        if not merchant:
            current_app.config['SENTRY_DSN'] and current_app.logger.fatal('invalid domain: %s', domain.data)
            raise ValidationError("无效的域名: %s" % domain.data)

        self.merchant.data = merchant
