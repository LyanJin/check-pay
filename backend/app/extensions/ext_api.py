"""API对象初始化
"""
from flask import url_for
from flask_restplus import Api

from config import ServiceEnum, FLASK_ENV, EnvironEnum

authorizations = {
    "Bearer Auth": {
        'type': 'apiKey',
        "in": "header",
        'name': 'Authorization'
    }
}


class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        if FLASK_ENV == EnvironEnum.DEVELOPMENT.value:
            scheme = 'http'
        else:
            scheme = 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


api_cashier = MyApi(
    prefix="/api/cashier/v1",
    doc="/doc/cashier/v1",
    version='1.0',
    title='钱包API',
    security="Bearer Auth",
    authorizations=authorizations,
    description='后端提供给前端钱包页面调用的API'
)

api_backoffice = MyApi(
    prefix="/api/backoffice/v1",
    doc="/doc/backoffice/v1",
    version='1.0',
    security="Bearer Auth",
    authorizations=authorizations,
    title='管理后台API',
    description='后台提供给前端管理页面API'
)

api_callback = MyApi(
    prefix="/api/callback/v1",
    doc="/doc/callback/v1",
    version='1.0',
    title='支付回调API',
    description='第三方支付回调API'
)

api_gateway = MyApi(
    prefix="/api/gateway/v1",
    doc="/doc/gateway/v1",
    version='1.0',
    title='商户开放API',
    description='提供给商户侧的开放API'
)

api_merchantoffice = MyApi(
    prefix="/api/merchantoffice/v1",
    doc="/doc/merchantoffice/v1",
    version='1.0',
    security="Bearer Auth",
    authorizations=authorizations,
    title='商户后台API',
    description='提供给商户后台侧的API'
)

API_CONFIG = {
    ServiceEnum.CASHIER.value: api_cashier,
    ServiceEnum.BACKOFFICE.value: api_backoffice,
    ServiceEnum.CALLBACK.value: api_callback,
    ServiceEnum.GATEWAY.value: api_gateway,
    ServiceEnum.MERCHANTOFFICE.value: api_merchantoffice,
}
