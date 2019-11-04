import requests

from app.docs.doc_cashier.deposit_withdraw import OrderTransfer
from app.enums.trade import OrderStateEnum
from app.extensions import limiter
from app.extensions.ext_api import api_cashier as api
from flask_restplus import Resource

from app.forms.deposit_form import BestPayNotifyForm
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import InvalidOrderIdError, ResponseSuccess
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.models.order.order_tasks import OrderTransferLog

ns = api.namespace('deposit', description='用户充值')


# /api/cashier/v1/deposit/notify/deposit

@ns.route('/notify/deposit', endpoint='notify_deposit')
@ResponseDoc.response(ns, api)
class DepositNotify(Resource):
    method_decorators = [limiter.limit("1/second")]

    @ns.expect(OrderTransfer)
    def post(self):
        """
        best pay 交易通知
        :return:
        """
        form, error = BestPayNotifyForm().request_validate()
        if error:
            return error.as_response()
        # 判断订单号是否存在 不存在 或状态不为Init 则返回无效的订单号
        order_id = form.tx_id.data
        order = DepositTransactionCtl.get_order_by_order_id(order_id=order_id)

        if not order or order.state.name != OrderStateEnum.INIT.name:
            return InvalidOrderIdError().as_response()
        # 收款银行卡号
        # 发起人姓名
        # 充值金额
        # 备注
        # 充值时间
        # 状态

        if not OrderTransferLog.insert_transfer_log(
                order_id=order_id,
                amount='{:.2f}'.format(float(form.amount.data)),
                in_account=form.card_number.data,
                out_name=form.user_name.data):
            return InvalidOrderIdError(message="新增转账信息有误").as_response()

        return ResponseSuccess().as_response()
