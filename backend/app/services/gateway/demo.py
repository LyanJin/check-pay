import json
from decimal import Decimal

import requests
from flask import request, url_for, redirect
from flask_restplus import Resource

from app.constants.admin_ip import ADMIN_IP_WHITE_LIST
from app.enums.trade import PaymentTypeEnum, OrderSourceEnum, PaymentBankEnum, PayTypeEnum
from app.extensions import limiter
from app.libs.datetime_kit import DateTimeKit
from app.libs.decorators import check_ip_in_white_list
from app.libs.error_code import ResponseSuccess
from app.libs.ip_kit import IpKit
from app.libs.order_kit import OrderUtils
from app.libs.template_kit import TemplateKit
from app.libs.url_kit import UrlKit
from app.logics.gateway.sign_check import GatewaySign
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from config import MerchantEnum, MerchantDomainConfig
from app.services.gateway import api

ns = api.namespace('demo', description='模拟商户API调用')

DEBUG_LOG = False
method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]
# method_decorators = [limiter.limit("1/second")]


def request_config():
    merchant = MerchantEnum.TEST_API
    post_data = dict(
        merchant_id=merchant.value,
        user_ip=IpKit.get_remote_ip(),
    )
    post_data['sign'] = GatewaySign(merchant).generate_sign(post_data)
    post_data['user_id'] = '100'
    domain = MerchantDomainConfig.get_gateway_domain(merchant)
    url = UrlKit.join_host_path(url_for('gateway_config_get'), host=domain)
    rsp = requests.post(url, json=post_data)

    if rsp.status_code != 200:
        return None, "http请求失败，状态码：%s, url: %s" % (rsp.status_code, url)

    if rsp.json()['error_code'] != 200:
        return None, rsp.json()['message']

    return rsp.json()['data'], None


@ns.route('/merchant/deposit', endpoint='gateway_demo_merchant_deposit')
class DemoMerchantDeposit(Resource):
    method_decorators = method_decorators

    def get(self):

        def render_temp(**kwargs):
            kwargs['title'] = "模拟商户(%s)充值" % MerchantEnum.TEST_API.name
            return TemplateKit.render_template(
                "merchant_demo/demo_deposit.html",
                **kwargs,
            )

        kwargs = dict()
        if request.args.get('success') or request.args.get('error'):
            # 重定向过来的
            kwargs.update(request.args)
            if 'post_data' in kwargs:
                kwargs['post_data'] = json.loads(kwargs['post_data'])

        data, error = request_config()
        if error:
            kwargs['error'] = error
            return render_temp(**kwargs)

        kwargs['payment_types'] = data['payment_types']
        return render_temp(**kwargs)

    def post(self):

        merchant = MerchantEnum.TEST_API
        amount = Decimal(request.form['amount'])

        domain = MerchantDomainConfig.get_latest_domain(merchant)

        # 模拟商户发起支付请求
        scheme_host = UrlKit.get_scheme_host(host=domain)
        url = scheme_host + url_for('gateway_deposit_request')

        if not request.form['payment_type']:
            return redirect(scheme_host + url_for('gateway_demo_merchant_deposit', error="请选择支付类型"))

        payment_type = PaymentTypeEnum.from_name(request.form['payment_type'])

        # 模拟商户的回调URL
        notify_url = UrlKit.join_host_path(url_for('gateway_demo_notify'), host=domain)

        post_data = dict(
            merchant_id=merchant.value,
            amount=str(amount),
            mch_tx_id=OrderUtils.generate_mch_tx_id(DateTimeKit.get_cur_timestamp()),
            payment_type=payment_type.name,
            notify_url=notify_url,
            user_ip=IpKit.get_remote_ip(),
        )
        print('post_data:', post_data)

        post_data['sign'] = GatewaySign(merchant).generate_sign(post_data)
        post_data['redirect_url'] = "https://google.com"
        post_data['extra'] = json.dumps(dict(x=1, y=2))
        post_data['user_id'] = "100"

        print('post_data:', post_data)

        rsp = requests.post(url, json=post_data)
        if rsp.status_code != 200:
            return redirect(scheme_host + url_for('gateway_demo_merchant_deposit',
                                                  error="http请求失败，状态码：%s, url: %s" % (rsp.status_code, url)))

        if rsp.json()['error_code'] != 200:
            return redirect(scheme_host + url_for('gateway_demo_merchant_deposit', error=rsp.json()['message']))

        sys_tx_id = rsp.json()['data']['sys_tx_id']

        return redirect(scheme_host + url_for(
            'gateway_demo_merchant_deposit',
            success=True,
            post_data=json.dumps(post_data),
            notify_url=scheme_host + url_for('demo_deposit_notify', tx_id=sys_tx_id),
            redirect_url=rsp.json()['data']['redirect_url'],
            sys_tx_id=sys_tx_id,
            mch_tx_id=rsp.json()['data']['mch_tx_id'],
            valid_time=rsp.json()['data']['valid_time'],
        ))


@ns.route('/deposit/notify', endpoint='demo_deposit_notify')
class DemoDepositNotify(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        手动通知商户
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?tx_id=xx").as_response()

        try:
            tx_id = request.args['tx_id']
        except:
            return ResponseSuccess(message="请输入 tx_id=，系统交易ID").as_response()

        order = DepositTransactionCtl.get_order(tx_id)
        rst = DepositTransactionCtl.do_notify(
            order=order,
            op_account='somebody',
            comment="后台人工状态通知",
        )

        return ResponseSuccess(message=rst['msg']).as_response()


@ns.route('/merchant/withdraw', endpoint='gateway_demo_merchant_withdraw')
class DemoMerchantWithdraw(Resource):
    method_decorators = method_decorators

    def get(self):

        def render_temp(**kwargs):
            kwargs['title'] = "模拟商户(%s)提现" % MerchantEnum.TEST_API.name
            return TemplateKit.render_template(
                "merchant_demo/demo_withdraw.html",
                **kwargs,
            )

        kwargs = dict()
        if request.args.get('success') or request.args.get('error'):
            # 重定向过来的
            kwargs.update(request.args)
            if 'post_data' in kwargs:
                kwargs['post_data'] = json.loads(kwargs['post_data'])

        data, error = request_config()
        if error:
            kwargs['error'] = error
            return render_temp(**kwargs)

        kwargs['bank_types'] = PaymentBankEnum.get_desc_name_pairs()
        kwargs['withdraw_config'] = data['withdraw_config']
        return render_temp(**kwargs)

    def post(self):

        merchant = MerchantEnum.TEST_API
        amount = Decimal(request.form['amount'])

        domain = MerchantDomainConfig.get_latest_domain(merchant)
        # 模拟商户发起支付请求
        scheme_host = UrlKit.get_scheme_host(host=domain)
        url = scheme_host + url_for('gateway_withdraw_request')

        if not request.form['bank_type']:
            return redirect(scheme_host + url_for('gateway_demo_merchant_withdraw', error="必选选择银行类型"))

        bank_type = PaymentBankEnum.from_name(request.form['bank_type'])

        # 模拟商户的回调URL
        notify_url = UrlKit.join_host_path(url_for('gateway_demo_notify'), host=domain)

        post_data = dict(
            merchant_id=merchant.value,
            amount=str(amount),
            mch_tx_id=OrderUtils.generate_mch_tx_id(DateTimeKit.get_cur_timestamp()),
            bank_type=bank_type.name,
            notify_url=notify_url,
            card_no=request.form['card_no'],
            account_name=request.form['account_name'],
            province=request.form['province'],
            city=request.form['city'],
            user_ip=IpKit.get_remote_ip(),
        )
        print('post_data:', post_data)

        post_data['sign'] = GatewaySign(merchant).generate_sign(post_data)
        post_data['extra'] = json.dumps(dict(x=1, y=2))
        post_data['user_id'] = "100"
        post_data['branch'] = request.form['branch']

        print('post_data:', post_data)

        rsp = requests.post(url, json=post_data)
        if rsp.status_code != 200:
            return redirect(scheme_host + url_for('gateway_demo_merchant_withdraw',
                                                  error="http请求失败，状态码：%s, url: %s" % (rsp.status_code, url)))

        if rsp.json()['error_code'] != 200:
            return redirect(scheme_host + url_for('gateway_demo_merchant_withdraw', error=rsp.json()['message']))

        sys_tx_id = rsp.json()['data']['sys_tx_id']

        return redirect(scheme_host + url_for(
            'gateway_demo_merchant_withdraw',
            success=True,
            post_data=json.dumps(post_data),
            notify_url=scheme_host + url_for('demo_withdraw_notify', tx_id=sys_tx_id),
            sys_tx_id=sys_tx_id,
            mch_tx_id=rsp.json()['data']['mch_tx_id'],
        ))


@ns.route('/withdraw/notify', endpoint='demo_withdraw_notify')
class DemoDepositRequest(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        手动通知商户
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?tx_id=xx").as_response()

        try:
            tx_id = request.args['tx_id']
        except:
            return ResponseSuccess(message="请输入 tx_id=，系统交易ID").as_response()

        order = WithdrawTransactionCtl.get_order(tx_id)
        rst = WithdrawTransactionCtl.do_notify(
            order=order,
            op_account='somebody',
            comment="后台人工状态通知",
        )

        return ResponseSuccess(message=rst['msg']).as_response()
