from decimal import Decimal

from flask import g, current_app
from flask_restplus import Resource
from sqlalchemy import or_

from app.caches.user_flag import UserFlagCache
from app.docs.doc_internal.merchant import QueryWithdrawOrderListDoc, AllowedOrder, WithDrawChannelAllowed, \
    UserBankExpect, WithDrawGetBankParams, WithDrawPersonExecuteParams, \
    WithDrawPersonExecuteDoneParams, YearMouthExpect, QueryDepositOrderListDoc, CreateDepositOrderParams, \
    OrderIdCommentDoc
from app.docs.doc_internal.trade_manage import AllWithdrawResult, ReviewWithdrawResult, WithdrawChannelResult, \
    WithdrawOrderDetailResult, WithdrawBankEntryResult, DepositOrderResult, DepositOrderDetailResult, \
    BackOfficeConfigResult, OrderStateNotifyDoc
from app.enums.trade import OrderStateEnum, PaymentTypeEnum, DeliverStateEnum
from app.extensions.ext_api import api_backoffice as api
from app.forms.backoffice.merchant import WithdrawOrderPerformForm, YearMouthForm, CreateDepositOrderForm, \
    OrderStateNotifyFrom, OrderIdCommentForm
from app.libs.error_code import NotAllocOrderError, InvalidChannelError, WithdrawBankNoExistError, \
    FailedLaunchWithdrawError, WithdrawUpdateDealingError
from app.libs.geo_ip.geo_ip import GeoIpKit
from app.libs.model.mix import MerchantMonthMix
from app.forms.backoffice.merchant import WithDrawSelectResultForm, WithDrawOrderAllowedForm, \
    WithDrawSupperBankForm, WithDrawBankForm, WithDrawPersonExecutedDoneForm, DepositOrderListSelectResultForm
from app.libs.doc_response import ResponseDoc
from app.libs.error_code import ResponseSuccess, NoSuchWithdrawOrderError, NoSuchOpeUserError, \
    BankOrderStateError, BankInfoMissingError, OrderInfoMissingError, AccountNotExistError, InvalidDepositChannelError, \
    ChannelNoValidityPeriodError, DepositOrderAmountInvalidError, MerchantConfigDepositError, PreOrderCreateError, \
    InvalidDepositPaymentTypeError
from app.logics.backoffice.order_list_helper import OrderListQueryHelper
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.channel import ProxyChannelConfig
from app.models.order.order import OrderWithdraw, OrderDeposit
from app.logics.token.admin_token import admin_decorators, get_admin_decorators
from app.libs.datetime_kit import DateTimeKit
from app.models.order.order_blobal import GlobalOrderId
from app.models.order.order_detail import OrderDetailWithdraw, OrderDetailDeposit
from app.models.order.order_event import OrderEvent
from config import MerchantEnum
from app.models.channel import ChannelConfig
from app.logics.order.create_ctl import OrderCreateCtl
from app.models.user import User
from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum
from app.models.merchant import MerchantFeeConfig
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.extensions import db

ns = api.namespace('trade_manage', description='交易管理')


@ns.route('/withdraw/list')
@ResponseDoc.response(ns, api)
class WithdrawList(Resource):
    method_decorators = get_admin_decorators(limit_cond=None)

    @ns.expect(QueryWithdrawOrderListDoc)
    @ns.marshal_with(AllWithdrawResult.gen_doc(api), as_list=True)
    def post(self):
        """
        提现订单列表
        :return:
        """
        form, error = WithDrawSelectResultForm().request_validate()
        if error:
            return error.as_response()

        return OrderListQueryHelper.query_withdraw_order_list(form)


@ns.route('/withdraw/list/export')
class WithdrawListExport(Resource):
    method_decorators = admin_decorators

    @ns.expect(QueryWithdrawOrderListDoc)
    def post(self):
        """
        导出CSV：提现订单列表
        :return:
        """
        form, error = WithDrawSelectResultForm().request_validate()
        if error:
            return error.as_response()

        return OrderListQueryHelper.query_withdraw_order_list(form, export=True)


@ns.route('/order/allowed')
@ResponseDoc.response(ns, api)
class AllowedOrderResource(Resource):
    method_decorators = admin_decorators

    @ns.expect(AllowedOrder)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        提现订单： 运营人员认领订单
        :return:
        """
        form, error = WithDrawOrderAllowedForm().request_validate()
        if error:
            return error.as_response()

        order_id = form.order_id.data
        merchant = form.merchant_name.data

        rst = WithdrawTransactionCtl.order_alloc(
            g.user.account, order_id, merchant
        )
        return rst.as_response()


@ns.route('/withdraw/review/list')
@ResponseDoc.response(ns, api)
class WithdrawReviewList(Resource):
    method_decorators = admin_decorators

    @ns.expect(YearMouthExpect)
    @ns.marshal_with(ReviewWithdrawResult.gen_doc(api), as_list=True)
    def post(self):
        """
        运营代付审核列表：
        :return:
        """

        form, error = YearMouthForm().request_validate()
        if error:
            return error.as_response()

        # 遍历系统所有商户
        begin_time, end_time = DateTimeKit.get_month_begin_end(year=int(form.year.data), month=int(form.mouth.data))
        if not MerchantMonthMix.is_valid_shard_date(begin_time):
            # 查询的时间太早，没有数据，直接返回空列表
            return ReviewWithdrawResult(bs_data=dict(
                entries=[], total=len([]), operator=g.user.account)).as_response()

        withdraw_list = []

        detail_list = OrderDetailWithdraw.query_by_create_time(begin_time=begin_time, end_time=end_time)
        detail_dict = dict([(o.order_id, o) for o in detail_list])

        order_list_query = OrderWithdraw.query_by_create_time(begin_time=begin_time, end_time=end_time)
        query = order_list_query.filter(or_(
            OrderWithdraw._state == OrderStateEnum.ALLOC.value,
            OrderWithdraw._state == OrderStateEnum.DEALING.value,
        )).all()

        for order in query:
            detail_order = detail_dict[order.order_id]
            if detail_order.op_account != g.user.account:
                continue

            bank = order.get_bank_card(valid_check=False)
            if not bank:
                current_app.logger.error('bank not exit, order.sys_tx_id: %s, order.bank_id: %s, order.bank_info: %s',
                                         order.sys_tx_id, order.bank_id, order.bank_info)
                continue

            user_flag = UserFlagCache(order.uid).get_flag()

            withdraw_list.append(dict(
                uid=order.uid,
                order_id=order.order_id,
                sys_tx_id=order.sys_tx_id,
                merchant=order.merchant.name,
                source=order.source.desc,
                state=order.state.desc,
                amount=order.amount,
                bank_name=bank.bank_name,
                bank_type=bank.bank_enum.name,
                create_time=order.str_create_time,
                user_flag=user_flag.name if user_flag else None,
            ))

        withdraw_list = sorted(
            withdraw_list, key=lambda item: item['create_time'])

        return ReviewWithdrawResult(bs_data=dict(
            entries=withdraw_list, total=len(withdraw_list), operator=g.user.account
        )).as_response()


@ns.route('/withdraw/launch')
@ResponseDoc.response(ns, api, [
    NoSuchOpeUserError, NoSuchWithdrawOrderError, NotAllocOrderError, WithdrawUpdateDealingError,
    InvalidChannelError, WithdrawBankNoExistError, FailedLaunchWithdrawError
])
class WithdrawLaunch(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithDrawChannelAllowed)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        运营发起确认对订单的提现，向第三方发起提现请求
        :return:
        """
        form, error = WithdrawOrderPerformForm().request_validate()
        if error:
            return error.as_response()

        merchant = form.merchant.data
        order_id = form.order_id.data
        channel_id = form.channel_id.data
        rst = WithdrawTransactionCtl.order_deal(
            g.user.account, order_id, merchant, channel_id
        )
        return rst.as_response()


@ns.route('/withdraw/available/channel')
@ResponseDoc.response(ns, api)
class WithdrawAvailableChannel(Resource):
    method_decorators = admin_decorators

    # 根据用户选择的银行，来确定当前可用的代付通道
    @ns.expect(UserBankExpect)
    @ns.marshal_with(WithdrawChannelResult.gen_doc(api))
    def post(self):
        """
        获取当前可用的代付通道
        """
        """
        1. 是否支持银行 banks like bank
        1. 提现金额 _limit_per_max, _limit_per_min
        2. 时间 _maintain_begin， _maintain_end
        """
        form, error = WithDrawSupperBankForm().request_validate()
        if error:
            return error.as_response()

        merchant = form.merchant_name.data
        channels = ProxyChannelConfig.query_all()
        proxy_channels = ProxyChannelConfig.filter_latest_items(channels)

        valid_channels = []
        withdraw_channel = {}

        for channel in proxy_channels:
            if form.bank_type.data not in channel.banks:
                continue

            if not channel.is_channel_valid(merchant.is_test, form.amount.data):
                continue

            withdraw_channel_key = channel.channel_enum.conf['provider'] + channel.channel_enum.conf['mch_id']
            withdraw_channel[withdraw_channel_key] = channel.channel_id
            valid_channels.append(channel)

        valid_channels = [dict(key=channel, value=withdraw_channel[channel])
                          for channel in withdraw_channel.keys()]

        return WithdrawChannelResult(bs_data=dict(entries=valid_channels)).as_response()


@ns.route('/withdraw/order/detail')
@ResponseDoc.response(ns, api)
class WithdrawOrderDetail(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithDrawGetBankParams)
    @ns.marshal_with(WithdrawOrderDetailResult.gen_doc(api), as_list=True)
    def post(self):
        """
        提现订单详情
        :return:
        """
        form, error = WithDrawBankForm().request_validate()
        if error:
            return error.as_response()

        order_id = form.order_id.data
        order_map = GlobalOrderId.query_global_id(order_id)
        merchant = order_map.merchant
        entry = OrderWithdraw.query_by_order_id(order_id=order_id, merchant=merchant)
        detail = OrderDetailWithdraw.query_by_order_id(merchant=merchant, order_id=order_id)
        detail_head = dict(
            source=entry.source.desc,
            op_account=detail.op_account,
            deliver_type=detail.deliver_type.desc if detail.deliver_type else None,
            create_time=entry.str_create_time,
            alloc_time=detail.str_alloc_time,
            deal_time=detail.str_deal_time,
            done_time=detail.str_done_time,
            mch_tx_id=entry.mch_tx_id,
            sys_tx_id=entry.sys_tx_id,
            state=entry.state.get_back_desc(PayTypeEnum.WITHDRAW),
            settle=entry.settle.desc,
            deliver=entry.deliver.desc,
            amount=entry.amount
        )
        order_merchant_info = dict(
            merchant_name=merchant.name,
            fee=detail.fee,
            cost=detail.cost,
            profit=detail.profit,
            withdraw_type="测试" if merchant.is_test else "用户提现"
        )
        deliver_info = None
        if entry.channel_id:
            proxy_entry = ProxyChannelConfig.query_by_channel_id(
                entry.channel_id)
            channel_enum = proxy_entry.channel_enum

            deliver_info = dict(
                channel_name=channel_enum.desc,
                mch_id=channel_enum.conf['mch_id'],
                channel_tx_id=entry.channel_tx_id
            )
        user_info = dict(
            user_id=entry.uid,
            ip=detail.ip,
            location=GeoIpKit(detail.ip).location,
            device="",
        )

        event_entries = OrderEvent.query_model(query_fields=dict(order_id=entry.order_id), date=entry.create_time)

        event_log_list = list()

        for event in event_entries:
            order_event = event.data_after[0]
            order_event.update(event.data_after[1])

            if 'state' in order_event:
                state = list(order_event['state'].keys())[0]
                event_log_list.append(dict(
                    operate_type=OrderStateEnum.from_name(state).get_back_desc(PayTypeEnum.WITHDRAW),
                    operator=order_event.get('op_account') or '',
                    result="成功",
                    operate_time=DateTimeKit.timestamp_to_datetime(order_event['update_time']),
                    comment=order_event.get('comment') or '',
                ))

            if 'deliver' in order_event:
                deliver = list(order_event['deliver'].keys())[0]
                event_log_list.append(dict(
                    operate_type=DeliverStateEnum.from_name(deliver).desc,
                    operator=order_event.get('op_account') or '',
                    result="成功",
                    operate_time=DateTimeKit.timestamp_to_datetime(order_event['update_time']),
                    comment=order_event.get('comment') or '',
                ))

        return WithdrawOrderDetailResult(bs_data=dict(
            detail_head=detail_head,
            order_merchant_info=order_merchant_info,
            deliver_info=deliver_info,
            user_info=user_info,
            event_log_list=event_log_list)
        ).as_response()


@ns.route('/withdraw/bank/info')
@ResponseDoc.response(ns, api)
class WithdrawBankInfo(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithDrawGetBankParams)
    @ns.marshal_with(WithdrawBankEntryResult.gen_doc(api), as_list=True)
    def post(self):
        """
        人工出款： 用户银行信息查询
        :return:
        """
        form, error = WithDrawBankForm().request_validate()
        if error:
            return error.as_response()

        # 查询 提现订单表 获取提现金额， 提现用户指定行
        order = OrderWithdraw.query_by_order_id(merchant=form.merchant.data, order_id=form.order_id.data)
        if not order:
            return OrderInfoMissingError().as_response()

        if order.state not in [OrderStateEnum.ALLOC, OrderStateEnum.DEALING]:
            return BankOrderStateError().as_response()

        bank = order.get_bank_card()
        if not bank:
            return BankInfoMissingError().as_response()

        bank_entry = dict(
            amount=order.amount,
            account_name=bank.account_name,
            card_no=bank.card_no,
            bank_name=bank.bank_name,
            province=bank.province,
            city=bank.city,
            branch=bank.branch
        )
        return WithdrawBankEntryResult(bs_data=dict(bank_entry=bank_entry)).as_response()


@ns.route('/withdraw/person/execute')
@ResponseDoc.response(ns, api)
class WithdrawPersonExecute(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithDrawPersonExecuteParams)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        人工出款： 运营手动转账出款
        :return:
        """
        form, error = WithDrawBankForm().request_validate()
        if error:
            return error.as_response()

        rsp = WithdrawTransactionCtl.manually_withdraw(
            admin_user=g.user,
            merchant=form.merchant.data,
            order_id=form.order_id.data,
        )

        return rsp.as_response()


@ns.route('/withdraw/person/done')
@ResponseDoc.response(ns, api)
class WithdrawPersonDone(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithDrawPersonExecuteDoneParams)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        运营确定出款成功
        :return:
        """
        form, error = WithDrawPersonExecutedDoneForm().request_validate()
        if error:
            return error.as_response()

        fee = form.fee.data if form.fee.data else "0"
        comment = form.comment.data

        rsp = WithdrawTransactionCtl.manually_withdraw_success(
            admin_user=g.user,
            merchant=form.merchant.data,
            order_id=form.order_id.data,
            channel_cost=fee,
            comment=comment,
        )

        return rsp.as_response()


@ns.route('/withdraw/refuse/reimburse')
@ResponseDoc.response(ns, api)
class WithdrawRefuseReimburse(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithDrawPersonExecuteParams)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        拒绝提现 或 提现失败
        :return:
        """
        form, error = WithDrawBankForm().request_validate()
        if error:
            return error.as_response()

        rsp = WithdrawTransactionCtl.manually_withdraw_failed(
            admin_user=g.user,
            merchant=form.merchant.data,
            order_id=form.order_id.data,
        )

        return rsp.as_response()


@ns.route('/deposit/order/list')
@ResponseDoc.response(ns, api)
class DepositOrderList(Resource):
    method_decorators = admin_decorators

    @ns.expect(QueryDepositOrderListDoc)
    @ns.marshal_with(DepositOrderResult.gen_doc(api), as_list=True)
    def post(self):
        """
        充值订单列表
        :return:
        """
        form, error = DepositOrderListSelectResultForm().request_validate()
        if error:
            return error.as_response()

        return OrderListQueryHelper.query_deposit_order_list(form)


@ns.route('/deposit/order/list/export')
class DepositOrderListExport(Resource):
    method_decorators = admin_decorators

    @ns.expect(QueryDepositOrderListDoc)
    def post(self):
        """
        导出CSV：充值订单列表
        :return:
        """
        form, error = DepositOrderListSelectResultForm().request_validate()
        if error:
            return error.as_response()

        return OrderListQueryHelper.query_deposit_order_list(form, export=True)


@ns.route('/deposit/order/detail')
@ResponseDoc.response(ns, api)
class DepositOrderDetail(Resource):
    method_decorators = admin_decorators

    # 期望的参数 用提款详情的
    @ns.expect(WithDrawGetBankParams)
    # 返回的数据结构
    @ns.marshal_with(DepositOrderDetailResult.gen_doc(api), as_list=True)
    def post(self):
        """
        充值订单详情
        :return:
        """
        # form表单验证用提款的
        form, error = WithDrawBankForm().request_validate()
        if error:
            return error.as_response()

        # 取得订单id
        order_id = form.order_id.data
        # 根据订单id获取对应的商户 用户id
        order_map = GlobalOrderId.query_global_id(order_id)
        # 获取商户id
        merchant = order_map.merchant

        # 根据商户id 订单id查询具体的订单信息
        entry = OrderDeposit.query_by_order_id(order_id=order_id, merchant=merchant)

        # 查询对应的订单详情表
        detail = OrderDetailDeposit.query_by_order_id(merchant=merchant, order_id=order_id)

        # 拼接返回数据
        detail_head = dict(
            source=entry.source.desc,
            create_time=entry.str_create_time,
            done_time=detail.str_done_time,
            mch_tx_id=entry.mch_tx_id,
            sys_tx_id=entry.sys_tx_id,
            state=entry.state.get_back_desc(PayTypeEnum.DEPOSIT),
            settle=entry.settle.desc,
            deliver=entry.deliver.desc,
            amount=entry.amount,
        )
        order_merchant_info = dict(
            merchant_name=merchant.name,
            offer=detail.offer,
            fee=detail.fee,
            cost=detail.cost,
            profit=detail.profit
        )
        deliver_info = None
        if entry.channel_id:
            proxy_entry = ChannelConfig.query_by_channel_id(
                entry.channel_id)
            channel_enum = proxy_entry.channel_enum

            deliver_info = dict(
                channel_name=channel_enum.desc,
                mch_id=channel_enum.conf['mch_id'],
                channel_tx_id=entry.channel_tx_id
            )
        user_info = dict(
            user_id=entry.uid,
            ip=detail.ip,
            location=GeoIpKit(detail.ip).location,
            device="",
        )

        event_entries = OrderEvent.query_model(query_fields=dict(order_id=entry.order_id), date=entry.create_time)

        event_log_list = list()

        for event in event_entries:
            order_event = event.data_after[0]
            order_event.update(event.data_after[1])

            if 'state' in order_event:
                state = list(order_event['state'].keys())[0]
                event_log_list.append(dict(
                    operate_type=OrderStateEnum.from_name(state).get_back_desc(PayTypeEnum.DEPOSIT),
                    operator=order_event.get('op_account') or '',
                    result="成功",
                    operate_time=DateTimeKit.timestamp_to_datetime(order_event['update_time']),
                    comment=order_event.get('comment') or '',
                ))

            if 'deliver' in order_event:
                deliver = list(order_event['deliver'].keys())[0]
                event_log_list.append(dict(
                    operate_type=DeliverStateEnum.from_name(deliver).desc,
                    operator=order_event.get('op_account') or '',
                    result="成功",
                    operate_time=DateTimeKit.timestamp_to_datetime(order_event['update_time']),
                    comment=order_event.get('comment') or '',
                ))

        return DepositOrderDetailResult(bs_data=dict(
            detail_head=detail_head,
            order_merchant_info=order_merchant_info,
            deliver_info=deliver_info,
            user_info=user_info,
            event_log_list=event_log_list),
        ).as_response()


@ns.route('/deposit/order/create')
@ResponseDoc.response(ns, api)
class CreateDepositOrder(Resource):
    method_decorators = admin_decorators

    # 期望的参数
    @ns.expect(CreateDepositOrderParams)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        手动补单
        :return:
        """
        form, error = CreateDepositOrderForm().request_validate()
        if error:
            return error.as_response()

        '''
        根据商户查询用户是否存在
        构造数据
        创建充值订单
        更改订单状态为完成
        '''
        # 根据商户查询用户是否存在
        user = User.query_user(
            form.merchant.data, uid=form.uid.data)
        if not user:
            return AccountNotExistError().as_response()

        # 构造数据
        client_ip = form.client_ip.data
        channel_enum = form.channel_id.data
        payment_type = form.payment_type.data
        amount = Decimal(form.amount.data)

        # 判断当前传入的支付类型是否该渠道支持
        if payment_type != channel_enum.conf['payment_type']:
            return InvalidDepositPaymentTypeError()

        merchant = form.merchant.data

        # 找出最新版本的商户费率配置
        channel_config = ChannelConfig.query_latest_one(query_fields=dict(channel_enum=channel_enum))
        if not channel_config:
            return InvalidDepositChannelError().as_response()

        if not channel_config.is_channel_valid(merchant.is_test):
            return ChannelNoValidityPeriodError().as_response()

        if ChannelListHelper.is_amount_out_of_range(amount=amount, merchant=merchant,
                                                    payment_way=PayTypeEnum.DEPOSIT, client_ip=client_ip):
            return DepositOrderAmountInvalidError().as_response()

        # limit_min, limit_max = ChannelLimitCacheCtl(
        #     PayTypeEnum.DEPOSIT).get_channel_limit()
        # try:
        #     if limit_min > amount or limit_max < amount:
        #         return DepositOrderAmountInvalidError().as_response()
        # except Exception as e:
        #     return MustRequestDepositLimitError().as_response()

        # 找出最新版本的商户费率配置
        merchant_fee = MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=merchant,
            payment_way=PayTypeEnum.DEPOSIT,
            payment_method=channel_enum.conf.payment_method
        ))

        if not merchant_fee:
            return MerchantConfigDepositError().as_response()

        try:
            with db.auto_commit():
                # 创建待支付订单
                order, _ = OrderCreateCtl.create_order_event(
                    uid=user.uid,
                    merchant=merchant,
                    amount=amount,
                    channel_id=channel_config.channel_id,
                    mch_fee_id=merchant_fee.config_id,
                    order_type=PayTypeEnum.DEPOSIT,
                    source=OrderSourceEnum.MANUALLY,
                    in_type=InterfaceTypeEnum.CASHIER_H5,
                    ip=client_ip,
                    pay_method=channel_enum.conf.payment_method,
                    op_account=g.user.account,  # 后台管理员账号，后台人工修改数据时必填
                    comment=form.remark.data,  # 管理后台修改备注，后台人工修改数据时必填
                    mch_tx_id=form.mch_tx_id.data,
                    commit=False,
                )
                if not order:
                    raise Exception('order create failed')

                # 支付成功
                if not DepositTransactionCtl.success_order_process(
                        order=order,
                        tx_amount=amount,
                        channel_tx_id=form.mch_tx_id.data,
                        comment="手动补单订单",
                        commit=False,
                ):
                    raise Exception('order process failed')
        except Exception as e:
            if str(e).find("Duplicate entry") >= 0:
                return PreOrderCreateError(message="商户订单号重复: {}".format(form.mch_tx_id.data)).as_response()
            return PreOrderCreateError(message=str(e)).as_response()

        return ResponseSuccess().as_response()


@ns.route('/backoffice/config/get')
@ResponseDoc.response(ns, api)
class BackofficeConfigGet(Resource):
    method_decorators = admin_decorators

    # 期望的参数

    @ns.marshal_with(BackOfficeConfigResult.gen_doc(api), as_list=True)
    def post(self):
        """
        后台配置信息
        :return:
        """
        # 获取 充值通道信息
        channel_list = []
        channels = ChannelConfig.query_all()
        channels = ChannelConfig.filter_latest_items(channels)
        for channel in channels:
            channel_enum = channel.channel_enum
            channel_list.append(dict(desc=channel_enum.desc, value=channel_enum.value))

        # 获取商户数据
        merchant_list = [dict(desc=m.name, value=m.value) for m in MerchantEnum]
        # 获取支付类型
        payment_type_list = [dict(desc=p.desc, value=p.value) for p in PaymentTypeEnum]

        return BackOfficeConfigResult(bs_data=dict(merchant=merchant_list,
                                                   payment_type=payment_type_list,
                                                   deposit_channel=channel_list)).as_response()


@ns.route('/order/notify')
@ResponseDoc.response(ns, api)
class OrderStateNotifyResource(Resource):
    method_decorators = admin_decorators

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

        order_id = form.order_id.data
        order_type = form.order_type.data

        if order_type == PayTypeEnum.WITHDRAW:
            order = WithdrawTransactionCtl.get_order_by_order_id(order_id)
            rst = WithdrawTransactionCtl.do_notify(
                order=order,
                op_account=g.user.account,
                comment="后台人工状态通知",
            )
        else:
            order = DepositTransactionCtl.get_order_by_order_id(order_id)
            rst = DepositTransactionCtl.do_notify(
                order=order,
                op_account=g.user.account,
                comment="后台人工状态通知",
            )

        return ResponseSuccess(message=rst['msg'])


@ns.route('/order/manually/done')
@ResponseDoc.response(ns, api)
class OrderManuallyDone(Resource):
    method_decorators = admin_decorators

    @ns.expect(OrderIdCommentDoc)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        人工完成充值订单
        :return:
        """
        form, error = OrderIdCommentForm().request_validate()
        if error:
            return error.as_response()

        order_id = form.order_id.data
        g_order_id = GlobalOrderId.query_global_id(order_id)

        order = OrderDeposit.query_by_order_id(merchant=g_order_id.merchant, order_id=order_id)

        if DepositTransactionCtl.success_order_process(order, order.amount, comment=form.comment.data,
                                                       op_account=g.user.account):
            return ResponseSuccess(message="处理成功")
        else:
            return ResponseSuccess(message="处理失败")
