from flask import g
from flask_restplus import Resource

from app.constants.cashier import TRANSACTION_PAGE_SIZE
from app.docs.doc_cashier.deposit_withdraw import UserOrderSelect, ResponseOrderEntryList
from app.forms.deposit_form import UserOrderSelectForm
from app.libs.datetime_kit import DateTimeKit
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import SelectDepositWithdrawDateError
from app.libs.model.mix import MerchantMonthMix
from app.logics.order.order_list import TransactionListHelper
from app.logics.token.cashier_token import get_cashier_decorators
from . import api

ns = api.namespace('order', description='订单列表')


@ns.route('/list')
@ResponseDoc.response(ns, api)
class UserOrderListView(Resource):
    method_decorators = get_cashier_decorators()

    # 相应数据格式
    @ns.expect(UserOrderSelect)
    @ns.marshal_with(ResponseOrderEntryList.gen_doc(api))
    def post(self):
        """
        获取用户交易历史记录
        """
        form, error = UserOrderSelectForm().request_validate()
        if error:
            return error.as_response()

        uid = g.user.uid
        merchant = g.user.merchant

        try:
            begin_time, end_time = DateTimeKit.get_month_begin_end(int(form.year.data), int(form.mouth.data))
        except Exception as e:
            return SelectDepositWithdrawDateError().as_response()

        if not MerchantMonthMix.is_valid_shard_date(begin_time):
            # 查询的时间太早，没有数据，直接返回空列表
            return ResponseOrderEntryList(
                bs_data=dict(order_entry_list=[], order_entry_total=0)).as_response()

        order_entry_list, order_entry_total = TransactionListHelper.get_transaction_list(
            form.payment_type.data, uid, merchant, begin_time, end_time, TRANSACTION_PAGE_SIZE, form.page_index.data
        )

        return ResponseOrderEntryList(bs_data=dict(
            order_entry_list=order_entry_list,
            order_entry_total=order_entry_total
        )).as_response()
