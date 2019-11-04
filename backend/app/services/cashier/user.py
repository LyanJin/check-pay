# -*-coding:utf8-*-
from flask import g
from flask_restplus import Resource

from app.docs.doc_cashier.deposit_withdraw import ResponseUserBalance
from app.libs.balance_kit import BalanceKit
from app.libs.doc_response import ResponseDoc
from app.extensions.ext_api import api_cashier as api
from app.logics.token.cashier_token import cashier_decorators
from app.models.balance import UserBalance


ns = api.namespace('user', description='用户操作')


@ns.route('/balance/get', endpoint='get_user_balance')
@ResponseDoc.response(ns, api)
class BalanceGetView(Resource):
    method_decorators = cashier_decorators

    # 相应数据格式
    @ns.marshal_with(ResponseUserBalance.gen_doc(api))
    def post(self):
        """
        获取用户余额
        """
        # uid = g.user.uid
        # merchant = g.user.merchant
        # account = g.user.account
        # is_active = g.user.is_active
        # state = g.user.state
        # ac_type = g.user.ac_type
        # login_pwd = g.user.login_pwd

        balance = UserBalance.query_balance(uid=g.user.uid, merchant=g.user.merchant).first()
        return ResponseUserBalance(bs_data=dict(
            balance=BalanceKit.divide_unit(balance.balance),
            has_trade_pwd=g.user.has_trade_pwd()
        )).as_response()
