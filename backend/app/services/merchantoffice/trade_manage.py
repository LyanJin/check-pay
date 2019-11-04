from app.docs.doc_merchantoffice.auth_login import MerchantBaseInfoResponse, MerchantOrderDeposit, \
    MerchantDepositOrderResult, MerchantOrderWithDraw, MerchantWithdrawOrderResult, OrderStateNotifyDoc
from app.enums.trade import PayTypeEnum
from app.libs.csv_kit import CsvKit
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.libs.order_kit import OrderUtils
from . import api
from app.forms.merchantoffice.auth_login import DepositOrderSelectForm, WithdrawOrderSelectForm, OrderStateNotifyFrom
from app.libs.balance_kit import BalanceKit
from app.libs.doc_response import ResponseDoc
from flask_restplus import Resource
from flask import g

from app.libs.error_code import MerchantInfoNoExistError, MultiMonthQueryError, ResponseSuccess
from app.libs.model.mix import MultiMonthQueryException
from app.logics.token.merchant_token import merchant_decorators
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.bankcard import BankCard
from app.models.channel import ChannelConfig
from app.models.merchant import MerchantInfo
from app.models.order.order import OrderDeposit, OrderWithdraw
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw
from config import MerchantEnum

ns = api.namespace('merchant_manage', description='商户管理后台')


@ns.route('/merchant/Index', endpoint='merchant_Index')
@ResponseDoc.response(ns, api)
class MerchantIndex(Resource):
    method_decorators = merchant_decorators

    @ns.marshal_with(MerchantBaseInfoResponse.gen_doc(api))
    def post(self):
        """
        商户基本信息
        :return:
        """
        user = g.user
        info = MerchantInfo.query_merchant(MerchantEnum(user.mid))
        if not info:
            return MerchantInfoNoExistError().as_response()

        merchant_info = dict(
            account=user.account,
            balance_total=info.balance_total,
            available_balance=info.balance_available,
            incoming_balance=info.balance_income,
            frozen_balance=info.balance_frozen
        )
        return MerchantBaseInfoResponse(bs_data=merchant_info).as_response()


@ns.route('/select/order/deposit', endpoint='order_deposit')
@ResponseDoc.response(ns, api)
class MerchantDeposit(Resource):
    method_decorators = merchant_decorators

    @ns.expect(MerchantOrderDeposit)
    @ns.marshal_with(MerchantDepositOrderResult.gen_doc(api))
    def post(self):
        """
        商户充值订单查询
        :return:
        """
        form, error = DepositOrderSelectForm().request_validate()
        if error:
            return error.as_response()

        user = g.user

        try:
            order_list_query = OrderDeposit.query_by_create_time(begin_time=form.start_datetime.data,
                                                                 end_time=form.end_datetime.data,
                                                                 merchant=MerchantEnum(user.mid))
        except MultiMonthQueryException as e:
            return MultiMonthQueryError().as_response()

        kwargs = {}
        tx_id = form.order_id.data
        if tx_id:
            if OrderUtils.is_sys_tx_id(tx_id):
                kwargs["sys_tx_id"] = tx_id
            else:
                kwargs["mch_tx_id"] = tx_id

        if form.state.data != "0":
            kwargs["_state"] = form.state.data.value

        query = order_list_query.filter_by(**kwargs)
        pagination = query.paginate(
            form.page_index.data, form.page_size.data, False)

        entries = pagination.items
        total = pagination.total

        items = []
        channel_lst = list(set([o.channel_id for o in entries]))
        channel_items = {Channel.id: Channel for Channel in
                         ChannelConfig.query.filter(ChannelConfig.id.in_(channel_lst)).all()}
        kwargs = {}
        if tx_id and entries:
            kwargs['id'] = entries[0].order_id
        order_items = {item.id: item for item in
                       OrderDetailDeposit.query_by_create_time(begin_time=form.start_datetime.data,
                                                               end_time=form.end_datetime.data,
                                                               merchant=MerchantEnum(user.mid)).filter_by(
                           **kwargs).all()}
        for order in entries:
            item_channel = channel_items.get(order.channel_id, {})
            detail = order_items.get(order.order_id, {})
            if not item_channel or not detail:
                continue

            items.append(dict(
                mch_tx_id=order.mch_tx_id,
                sys_tx_id=order.sys_tx_id,
                payment_type=item_channel.channel_enum.conf['payment_type'].desc,
                amount=detail.amount,
                tx_amount=detail.tx_amount,
                fee=detail.fee,
                create_time=order.str_create_time,
                done_time=order.update_time,
                state=order.state.desc,
                deliver=order.deliver.desc
            ))
        items = sorted(items, key=lambda item: item['create_time'])
        return MerchantDepositOrderResult(bs_data=dict(entries=items, total=total)).as_response()


@ns.route('/select/order/withdraw', endpoint='order_withdraw')
@ResponseDoc.response(ns, api)
class MerchantWithdraw(Resource):
    method_decorators = merchant_decorators

    @ns.expect(MerchantOrderWithDraw)
    @ns.marshal_with(MerchantWithdrawOrderResult.gen_doc(api))
    def post(self):
        """
        商户提现订单查询
        :return:
        """
        form, error = WithdrawOrderSelectForm().request_validate()
        if error:
            return error.as_response()

        user = g.user

        try:
            order_list_query = OrderWithdraw.query_by_create_time(begin_time=form.start_datetime.data,
                                                                  end_time=form.end_datetime.data,
                                                                  merchant=MerchantEnum(user.mid))

        except MultiMonthQueryException as e:
            return MultiMonthQueryError().as_response()

        kwargs = {}
        tx_id = form.order_id.data
        if tx_id:
            if OrderUtils.is_sys_tx_id(tx_id):
                kwargs["sys_tx_id"] = tx_id
            else:
                kwargs["mch_tx_id"] = tx_id

        if form.state.data != "0":
            kwargs["_state"] = form.state.data.value

        query = order_list_query.filter_by(**kwargs)
        pagination = query.paginate(
            form.page_index.data, form.page_size.data, False)

        entries = pagination.items
        total = pagination.total

        bank_lst = list(set([o.bank_id for o in entries]))
        kwargs = {}

        if tx_id and entries:
            kwargs['id'] = entries[0].order_id

        bank_items = dict()
        if not MerchantEnum(user.mid).is_api_merchant:
            bank_items = {bank.id: bank for bank in BankCard.query.filter(BankCard.id.in_(bank_lst)).all()}
        order_items = {item.id: item for item in
                       OrderDetailWithdraw.query_by_create_time(begin_time=form.start_datetime.data,
                                                                end_time=form.end_datetime.data,
                                                                merchant=MerchantEnum(user.mid)).filter_by(
                           **kwargs).all()}

        items = []
        for order in entries:
            if not MerchantEnum(user.mid).is_api_merchant:
                bank = bank_items.get(order.bank_id, {})
            else:
                bank = order.get_bank_card()
            detail = order_items.get(order.order_id, {})
            if not bank or not detail:
                continue
            items.append(dict(
                mch_tx_id=order.mch_tx_id,
                sys_tx_id=order.sys_tx_id,
                amount=detail.amount,
                fee=detail.fee,
                account_name=bank.account_name,
                bank_name=bank.bank_name,
                branch="{}{}{}".format(bank.province, bank.city, bank.branch),
                card_no=bank.card_no,
                create_time=order.str_create_time,
                done_time=order.update_time,
                state=order.state.desc,
                deliver=order.deliver.desc
            ))
        items = sorted(items, key=lambda item: item['create_time'])
        return MerchantWithdrawOrderResult(bs_data=dict(entries=items, total=total)).as_response()


@ns.route('/merchant/order/notify')
@ResponseDoc.response(ns, api)
class OrderStateNotifyResource(Resource):
    method_decorators = merchant_decorators

    @ns.expect(OrderStateNotifyDoc)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        给商户发通知
        :return:
        """
        form, error = OrderStateNotifyFrom().request_validate()
        if error:
            return error.as_response()

        order_id = str(form.order_id.data)
        if form.type.data == PayTypeEnum.WITHDRAW:
            order = WithdrawTransactionCtl.get_order(order_id)
            rst = WithdrawTransactionCtl.do_notify(
                order=order,
                op_account=g.user.account,
                comment="商户后台手动通知"
            )
        elif form.type.data == PayTypeEnum.DEPOSIT:
            order = DepositTransactionCtl.get_order(order_id)
            rst = DepositTransactionCtl.do_notify(
                order=order,
                op_account=g.user.account,
                comment="商户后台手动通知",
            )

        return ResponseSuccess(message=rst['msg'])


@ns.route('/select/order/withdraw/csv', endpoint='order_withdraw_csv')
class MerchantWithdrawCsv(Resource):
    method_decorators = merchant_decorators

    @ns.expect(MerchantOrderWithDraw)
    def post(self):
        """
        商户提现订单查询
        :return:
        """
        form, error = WithdrawOrderSelectForm().request_validate()
        if error:
            return error.as_response()

        user = g.user

        try:
            order_list_query = OrderWithdraw.query_by_create_time(begin_time=form.start_datetime.data,
                                                                  end_time=form.end_datetime.data,
                                                                  merchant=MerchantEnum(user.mid))

        except MultiMonthQueryException as e:
            return MultiMonthQueryError().as_response()

        kwargs = {}
        if form.order_id.data:
            kwargs["mch_tx_id"] = form.order_id.data

        if form.state.data != "0":
            kwargs["_state"] = form.state.data.value

        entries = order_list_query.filter_by(**kwargs).all()

        bank_lst = list(set([o.bank_id for o in entries]))
        kwargs = {}

        if form.order_id.data and entries:
            kwargs['id'] = entries[0].order_id
        if not MerchantEnum(user.mid).is_api_merchant:
            bank_items = {bank.id: bank for bank in BankCard.query.filter(BankCard.id.in_(bank_lst)).all()}
        order_items = {item.id: item for item in
                       OrderDetailWithdraw.query_by_create_time(begin_time=form.start_datetime.data,
                                                                end_time=form.end_datetime.data,
                                                                merchant=MerchantEnum(user.mid)).filter_by(
                           **kwargs).all()}

        items = []
        for order in entries:
            if not MerchantEnum(user.mid).is_api_merchant:
                bank = bank_items.get(order.bank_id, {})
            else:
                bank = order.get_bank_card()
            detail = order_items.get(order.order_id, {})
            if not bank or not detail:
                continue
            items.append(dict(
                mch_tx_id=order.mch_tx_id,
                sys_tx_id=order.sys_tx_id,
                amount=detail.amount,
                fee=detail.fee,
                account_name=bank.account_name,
                bank_name=bank.bank_name,
                branch="{}{}{}".format(bank.province, bank.city, bank.branch),
                card_no=bank.card_no,
                create_time=order.str_create_time,
                done_time=order.update_time,
                state=order.state.desc,
                deliver=order.deliver.desc
            ))
        items = sorted(items, key=lambda item: item['create_time'])

        if items:
            data = list()
            for item in items:
                data.append(
                    {
                        "商户订单号": item['mch_tx_id'],
                        "提现金额": str(item['amount']),
                        "手续费": str(item['fee']),
                        "开户名": item['account_name'],
                        "开户银行": item['bank_name'],
                        "开户地址": item['branch'],
                        "银行卡号": item['card_no'],
                        "创建时间": item['create_time'],
                        "完成时间": item['done_time'],
                        "订单状态": item['state'],
                        "通知状态": item['deliver']
                    }
                )

            filename = 'epay_withdraw_record_%s.csv' % (DateTimeKit.datetime_to_str(
                DateTimeKit.get_cur_datetime(),
                DateTimeFormatEnum.TIGHT_DAY_FORMAT
            ))

            return CsvKit.send_csv(data, filename=filename, fields=data[0].keys())


@ns.route('/select/order/deposit/csv', endpoint='order_deposit_csv')
class MerchantDepositCsv(Resource):
    method_decorators = merchant_decorators

    @ns.expect(MerchantOrderDeposit)
    def post(self):
        """
        商户充值订单查询数据导出
        :return:
        """
        form, error = DepositOrderSelectForm().request_validate()
        if error:
            return error.as_response()

        user = g.user

        try:
            order_list_query = OrderDeposit.query_by_create_time(begin_time=form.start_datetime.data,
                                                                 end_time=form.end_datetime.data,
                                                                 merchant=MerchantEnum(user.mid))
        except MultiMonthQueryException as e:
            return MultiMonthQueryError().as_response()

        kwargs = {}
        if form.order_id.data:
            kwargs["sys_tx_id"] = form.order_id.data

        if form.state.data != "0":
            kwargs["_state"] = form.state.data.value

        entries = order_list_query.filter_by(**kwargs).all()

        items = []
        channel_lst = list(set([o.channel_id for o in entries]))
        channel_items = {Channel.id: Channel for Channel in
                         ChannelConfig.query.filter(ChannelConfig.id.in_(channel_lst)).all()}
        kwargs = {}
        if form.order_id.data and entries:
            kwargs['id'] = entries[0].order_id
        order_items = {item.id: item for item in
                       OrderDetailDeposit.query_by_create_time(begin_time=form.start_datetime.data,
                                                               end_time=form.end_datetime.data,
                                                               merchant=MerchantEnum(user.mid)).filter_by(
                           **kwargs).all()}
        for order in entries:
            item_channel = channel_items.get(order.channel_id, {})
            detail = order_items.get(order.order_id, {})
            if not item_channel or not detail:
                continue

            items.append(dict(
                mch_tx_id=order.mch_tx_id,
                sys_tx_id=order.sys_tx_id,
                payment_type=item_channel.channel_enum.conf['payment_type'].desc,
                amount=detail.amount,
                tx_amount=detail.tx_amount,
                fee=detail.fee,
                create_time=order.str_create_time,
                done_time=order.update_time,
                state=order.state.desc,
                deliver=order.deliver.desc
            ))
        items = sorted(items, key=lambda item: item['create_time'])

        if items:
            data = list()
            for item in items:
                data.append(
                    {
                        "商户订单号": item['mch_tx_id'],
                        "支付方式": item['payment_type'],
                        "发起金额": str(item['amount']),
                        "实际支付金额": str(item['tx_amount']),
                        "手续费": str(item['fee']),
                        "创建时间": item['create_time'],
                        "完成时间": item['done_time'],
                        "订单状态": item['state'],
                        "通知状态": item['deliver']
                    }
                )

            filename = 'epay_deposit_record_%s.csv' % (DateTimeKit.datetime_to_str(
                DateTimeKit.get_cur_datetime(),
                DateTimeFormatEnum.TIGHT_DAY_FORMAT
            ))

            return CsvKit.send_csv(data, filename=filename, fields=data[0].keys())
