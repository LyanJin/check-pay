from decimal import Decimal
from flask import current_app
from flask_restplus import Resource

from app.extensions.ext_api import api_backoffice as api
from app.libs.datetime_kit import DateTimeKit
from app.libs.doc_response import ResponseDoc
from app.libs.model.base import ModelBase
from app.enums.channel import ChannelConfigEnum
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.token.admin_token import admin_decorators
from app.models.channel import ChannelConfig, ChannelStateEnum, ProxyChannelConfig, ChannelRouter, ChannelRouter2
from app.docs.doc_internal.channel import ChannelListResult, ChannelAddList, WithdrawAddList, \
    ChannelConfigResult, WithdrawListResult, RuleListResult, RuleAddList, ResponseSuccess, RuleEditList, \
    ChannelConfigQueryDoc, RouterAddDoc
from app.forms.backoffice.channel import ChannelAddForm, WithdrawAddForm, ChannelRouterAddForm, \
    ChannelConfigQueryForm, ChannelRouterUpdateForm, ChannelRouter2AddForm, ChannelRouter2AddForm
from app.enums.trade import PaymentFeeTypeEnum, PaymentTypeEnum, PayMethodEnum, SettleTypeEnum, \
    PaymentBankEnum, InterfaceTypeEnum, PayTypeEnum
from sqlalchemy.exc import IntegrityError
from app.libs.error_code import ChannelSqlIntegrityError, DateStartMoreThanError, \
    DataStartMoreThanError, PerLimitMustLittleDayLimitError
from config import MerchantEnum

ns = api.namespace('channel', description='通道管理')


@ns.route('/config/get')
@ResponseDoc.response(ns, api)
class ChannelConfigGet(Resource):
    method_decorators = admin_decorators

    @ns.expect(ChannelConfigQueryDoc)
    @ns.marshal_with(ChannelConfigResult.gen_doc(api))
    def post(self):
        """
        通道管理： 获取通道配置信息
        :return:
        """
        form, error = ChannelConfigQueryForm().request_validate()
        if error:
            return error.as_response()

        pay_type = form.pay_type.data

        config_channels_dict = ChannelListHelper.get_config_channels(pay_type, ret_dict=True)

        if pay_type == PayTypeEnum.DEPOSIT:
            configs = [c for c in ChannelConfigEnum if c.value not in config_channels_dict and c.conf['payment_type']]
        else:
            configs = [c for c in ChannelConfigEnum if
                       c.value not in config_channels_dict and not c.conf['payment_type']]

        channel_config_list = [dict(
            channel_id=i.value,
            channel_desc=i.desc,
            id=i.conf["id"],
            provider=i.conf["provider"],
            name=i.conf["name"],
            payment_type=i.conf["payment_type"].desc if i.conf['payment_type'] else '',
            payment_method=i.conf["payment_method"].desc if i.conf['payment_method'] else '',
        ) for i in configs]

        data = dict(
            channel_config=channel_config_list,
            payment_fee_type=PaymentFeeTypeEnum.get_desc_value_pairs(),
            settlement_type=SettleTypeEnum.get_name_value_pairs(),
            channel_state=ChannelStateEnum.get_desc_value_pairs(),
            banks=PaymentBankEnum.get_desc_value_pairs(),
            # banks=[item.value for item in PaymentBankEnum],
            interfaces=InterfaceTypeEnum.get_name_value_pairs(),
            payment_method=PayMethodEnum.get_desc_value_pairs(),
            merchant_name=MerchantEnum.get_name_value_pairs(),
            payment_types=PaymentTypeEnum.get_desc_name_pairs(),
        )
        return ChannelConfigResult(bs_data=data).as_response()


@ns.route('/deposit/list')
@ResponseDoc.response(ns, api)
class ChannelList(Resource):
    method_decorators = admin_decorators

    @ns.marshal_with(ChannelListResult.gen_doc(api), as_list=True)
    def post(self):
        """
        充值通道列表
        :return:
        """

        router2_dict = ChannelListHelper.get_router2_dict()

        channel_list = []
        channels = ChannelConfig.query_all()
        channels = ChannelConfig.filter_latest_items(channels)
        for channel in channels:
            channel_enum = channel.channel_enum
            channel_conf = channel_enum.conf

            merchants = list()
            router = router2_dict.get(channel_enum)
            if router:
                merchants = router.merchants

            channel_list.append(dict(
                channel_id=channel_enum.value,
                channel_desc=channel_enum.desc,
                id=channel_conf['mch_id'],
                provider=channel_conf['provider'],
                payment_type=dict(desc=PaymentTypeEnum(channel_conf['payment_type']).desc,
                                  value=PaymentTypeEnum(channel_conf['payment_type']).value),
                payment_method=dict(desc=PayMethodEnum(channel_conf['payment_method']).desc,
                                    value=PayMethodEnum(channel_conf['payment_method']).value),
                fee=channel.fee,
                fee_type=dict(desc=PaymentFeeTypeEnum(channel.fee_type).desc,
                              value=PaymentFeeTypeEnum(channel.fee_type).value),
                limit_per_min=channel.limit_per_min,
                limit_per_max=channel.limit_per_max,
                limit_day_max=channel.limit_day_max,
                settlement_type=dict(key=SettleTypeEnum(channel.settlement_type).value,
                                     value=SettleTypeEnum(channel.settlement_type).name),
                trade_start_time=":".join([str(channel.trade_begin_hour), str(channel.trade_begin_minute)]),
                # trade_start_time=dict(trade_begin_hour=channel.trade_begin_hour,
                #                       trade_begin_minute=channel.trade_begin_minute),
                trade_end_time=":".join([str(channel.trade_end_hour), str(channel.trade_end_minute)]),
                # trade_end_time=dict(trade_end_hour=channel.trade_end_hour,
                #                     trade_end_minute=channel.trade_end_minute),
                main_time=dict(maintain_begin=channel.maintain_begin if channel.maintain_begin else None,
                               maintain_end=channel.maintain_end if channel.maintain_end else None),
                state=dict(
                    desc=channel.state.desc,
                    value=channel.state.value
                ),
                reason=channel.get_reason_desc(),
                priority=channel.priority,
                merchants=[x.name for x in merchants],
            ))
        channel_list = sorted(channel_list, key=lambda item: item['state']['value'])
        data = dict(counts=len(channel_list), channels=channel_list)

        return ChannelListResult(bs_data=data).as_response()


@ns.route('/deposit/add')
@ResponseDoc.response(ns, api)
class ChannelAdd(Resource):
    method_decorators = admin_decorators

    @ns.expect(ChannelAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        通道管理： 新建通道
        :return:
        """

        form, error = ChannelAddForm().request_validate()
        if error:
            return error.as_response()

        # if form.start_time.data >= form.end_time.data:
        #     return DateStartMoreThanError().as_response()

        if form.maintain_begin.data:
            if form.maintain_begin.data >= form.maintain_end.data or form.maintain_begin.data < DateTimeKit.get_cur_datetime():
                return DateStartMoreThanError().as_response()

        if Decimal(form.limit_per_min.data) >= Decimal(form.limit_per_max.data):
            return DataStartMoreThanError().as_response()

        if form.limit_day_max.data and Decimal(form.limit_per_max.data) > Decimal(form.limit_day_max.data):
            return PerLimitMustLittleDayLimitError().as_response()

        kwargs = dict(
            fee=form.fee.data,
            fee_type=form.fee_type.data,
            limit_per_min=form.limit_per_min.data,
            limit_per_max=form.limit_per_max.data,
            limit_day_max=form.limit_day_max.data if form.limit_day_max.data != "" else 0,
            trade_begin_hour=form.start_time.data.hour,
            trade_begin_minute=form.start_time.data.minute,
            trade_end_hour=form.end_time.data.hour,
            trade_end_minute=form.end_time.data.minute,
            maintain_begin=form.maintain_begin.data,
            maintain_end=form.maintain_end.data,
            settlement_type=form.settlement_type.data,
            state=form.state.data,
            priority=form.priority.data
        )

        rst, error = ChannelConfig.update_channel(form.channel_id.data, **kwargs)
        if error:
            return error.as_response()

        # 同步缓存
        # ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).sync_db_channels_to_cache()

        return ResponseSuccess().as_response()


@ns.route('/deposit/edit')
@ResponseDoc.response(ns, api)
class ChannelEdit(Resource):
    method_decorators = admin_decorators

    @ns.expect(ChannelAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        通道管理： 编辑通道
        :return:
        """
        form, error = ChannelAddForm().request_validate()
        if error:
            return error.as_response()

        # if form.start_time.data >= form.end_time.data:
        #     return DateStartMoreThanError().as_response()

        if form.maintain_begin.data:
            if form.maintain_begin.data >= form.maintain_end.data or form.maintain_begin.data < DateTimeKit.get_cur_datetime():
                return DateStartMoreThanError().as_response()

        if int(form.limit_per_min.data) >= int(form.limit_per_max.data):
            return DataStartMoreThanError().as_response()

        if form.limit_day_max.data and Decimal(form.limit_per_max.data) > Decimal(form.limit_day_max.data):
            return PerLimitMustLittleDayLimitError().as_response()

        kwargs = dict(
            fee=form.fee.data,
            fee_type=form.fee_type.data,
            limit_per_min=form.limit_per_min.data,
            limit_per_max=form.limit_per_max.data,
            limit_day_max=form.limit_day_max.data if form.limit_day_max.data != "" else 0,
            trade_begin_hour=form.start_time.data.hour,
            trade_begin_minute=form.start_time.data.minute,
            trade_end_hour=form.end_time.data.hour,
            trade_end_minute=form.end_time.data.minute,
            maintain_begin=form.maintain_begin.data,
            maintain_end=form.maintain_end.data,
            settlement_type=form.settlement_type.data,
            state=form.state.data,
            priority=form.priority.data
        )

        rst, error = ChannelConfig.update_channel(form.channel_id.data, **kwargs)
        if error:
            return error.as_response()

        # 同步缓存
        # ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).sync_db_channels_to_cache()

        return ResponseSuccess().as_response()


@ns.route('/deposit/del')
@ResponseDoc.response(ns, api)
class ChannelDel(Resource):
    method_decorators = admin_decorators

    @ns.expect(ChannelAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        通道管理： 删除通道
        :return:
        """
        form, error = ChannelAddForm().request_validate()
        if error:
            return error.as_response()

        # if form.start_time.data >= form.end_time.data:
        #     return DateStartMoreThanError().as_response()

        if form.maintain_begin.data:
            if form.maintain_begin.data >= form.maintain_end.data or form.maintain_begin.data < DateTimeKit.get_cur_datetime():
                return DateStartMoreThanError().as_response()

        if int(form.limit_per_min.data) >= int(form.limit_per_max.data):
            return DataStartMoreThanError().as_response()

        if form.limit_day_max.data and Decimal(form.limit_per_max.data) > Decimal(form.limit_day_max.data):
            return PerLimitMustLittleDayLimitError().as_response()

        kwargs = dict(
            fee=form.fee.data,
            fee_type=form.fee_type.data,
            limit_per_min=form.limit_per_min.data,
            limit_per_max=form.limit_per_max.data,
            limit_day_max=form.limit_day_max.data if form.limit_day_max.data != "" else 0,
            trade_begin_hour=form.start_time.data.hour,
            trade_begin_minute=form.start_time.data.minute,
            trade_end_hour=form.end_time.data.hour,
            trade_end_minute=form.end_time.data.minute,
            maintain_begin=form.maintain_begin.data,
            maintain_end=form.maintain_end.data,
            settlement_type=form.settlement_type.data,
            state=form.state.data,
            priority=form.priority.data,
            valid=ModelBase.INVALID
        )

        rst, error = ChannelConfig.update_channel(form.channel_id.data, **kwargs)
        if error:
            return error.as_response()

        # 同步缓存
        # ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).sync_db_channels_to_cache()

        return ResponseSuccess().as_response()


@ns.route('/withdraw/add')
@ResponseDoc.response(ns, api)
class WithdrawAdd(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithdrawAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        代付通道管理： 新建代付通道
        :return:
        """
        form, error = WithdrawAddForm().request_validate()

        if error:
            return error.as_response()

        if form.start_time.data >= form.end_time.data:
            return DateStartMoreThanError().as_response()

        if form.maintain_begin.data:
            if form.maintain_begin.data >= form.maintain_end.data or form.maintain_begin.data < DateTimeKit.get_cur_datetime():
                return DateStartMoreThanError().as_response()

        if Decimal(form.limit_per_min.data) >= Decimal(form.limit_per_max.data):
            return DataStartMoreThanError().as_response()

        if form.limit_day_max.data and Decimal(form.limit_per_max.data) > Decimal(form.limit_day_max.data):
            return PerLimitMustLittleDayLimitError().as_response()

        banks = [PaymentBankEnum(int(bank)) for bank in form.banks.data]

        kwargs = dict(
            fee=form.fee.data,
            fee_type=form.fee_type.data,
            limit_per_min=form.limit_per_min.data,
            limit_per_max=form.limit_per_max.data,
            limit_day_max=form.limit_day_max.data if form.limit_day_max.data != "" else 0,
            trade_begin_hour=form.start_time.data.hour,
            trade_begin_minute=form.start_time.data.minute,
            trade_end_hour=form.end_time.data.hour,
            trade_end_minute=form.end_time.data.minute,
            maintain_begin=form.maintain_begin.data if form.maintain_begin else "",
            maintain_end=form.maintain_end.data if form.maintain_end else "",
            state=form.state.data,
            banks=banks
        )

        rst, error = ProxyChannelConfig.update_channel(form.channel_id.data, **kwargs)
        if error:
            return error.as_response()

        # 同步缓存
        # ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).sync_db_channels_to_cache()

        return ResponseSuccess().as_response()


@ns.route('/withdraw/del')
@ResponseDoc.response(ns, api)
class WithdrawDel(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithdrawAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        代付通道管理： 删除代付通道
        :return:
        """
        form, error = WithdrawAddForm().request_validate()

        if error:
            return error.as_response()

        if form.start_time.data >= form.end_time.data:
            return DateStartMoreThanError().as_response()

        if form.maintain_begin.data:
            if form.maintain_begin.data >= form.maintain_end.data or form.maintain_begin.data < DateTimeKit.get_cur_datetime():
                return DateStartMoreThanError().as_response()

        if Decimal(form.limit_per_min.data) >= Decimal(form.limit_per_max.data):
            return DataStartMoreThanError().as_response()

        if form.limit_day_max.data and Decimal(form.limit_per_max.data) > Decimal(form.limit_day_max.data):
            return PerLimitMustLittleDayLimitError().as_response()

        banks = [PaymentBankEnum(int(bank)) for bank in form.banks.data]

        kwargs = dict(
            fee=form.fee.data,
            fee_type=form.fee_type.data,
            limit_per_min=form.limit_per_min.data,
            limit_per_max=form.limit_per_max.data,
            limit_day_max=form.limit_day_max.data if form.limit_day_max.data != "" else 0,
            trade_begin_hour=form.start_time.data.hour,
            trade_begin_minute=form.start_time.data.minute,
            trade_end_hour=form.end_time.data.hour,
            trade_end_minute=form.end_time.data.minute,
            maintain_begin=form.maintain_begin.data if form.maintain_begin else "",
            maintain_end=form.maintain_end.data if form.maintain_end else "",
            state=form.state.data,
            banks=banks,
            valid=ModelBase.INVALID
        )

        rst, error = ProxyChannelConfig.update_channel(form.channel_id.data, **kwargs)
        if error:
            return error.as_response()

        # 同步缓存
        # ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).sync_db_channels_to_cache()

        return ResponseSuccess().as_response()


@ns.route('/withdraw/edit')
@ResponseDoc.response(ns, api)
class WithdrawEdit(Resource):
    method_decorators = admin_decorators

    @ns.expect(WithdrawAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        代付通道管理： 编辑代付通道
        :return:
        """
        form, error = WithdrawAddForm().request_validate()

        if error:
            return error.as_response()

        if form.start_time.data >= form.end_time.data:
            return DateStartMoreThanError().as_response()

        if form.maintain_begin.data:
            if form.maintain_begin.data >= form.maintain_end.data or form.maintain_begin.data < DateTimeKit.get_cur_datetime():
                return DateStartMoreThanError().as_response()

        if Decimal(form.limit_per_min.data) >= Decimal(form.limit_per_max.data):
            return DataStartMoreThanError().as_response()

        if form.limit_day_max.data and Decimal(form.limit_per_max.data) > Decimal(form.limit_day_max.data):
            return PerLimitMustLittleDayLimitError().as_response()

        banks = [PaymentBankEnum(int(bank)) for bank in form.banks.data]

        kwargs = dict(
            fee=form.fee.data,
            fee_type=form.fee_type.data,
            limit_per_min=form.limit_per_min.data,
            limit_per_max=form.limit_per_max.data,
            limit_day_max=form.limit_day_max.data if form.limit_day_max.data != "" else 0,
            trade_begin_hour=form.start_time.data.hour,
            trade_begin_minute=form.start_time.data.minute,
            trade_end_hour=form.end_time.data.hour,
            trade_end_minute=form.end_time.data.minute,
            maintain_begin=form.maintain_begin.data if form.maintain_begin else "",
            maintain_end=form.maintain_end.data if form.maintain_end else "",
            state=form.state.data,
            banks=banks
        )

        rst, error = ProxyChannelConfig.update_channel(form.channel_id.data, **kwargs)
        if error:
            return error.as_response()

        # 同步缓存
        # ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).sync_db_channels_to_cache()

        return ResponseSuccess().as_response()


@ns.route('/withdraw/list')
@ResponseDoc.response(ns, api)
class WithdrawList(Resource):
    method_decorators = admin_decorators

    @ns.marshal_with(WithdrawListResult.gen_doc(api), as_list=True)
    def post(self):
        """
        代付通道管理： 代付通道列表
        :return:
        """
        channel_list = []
        channels = ProxyChannelConfig.query_all()
        channels = ProxyChannelConfig.filter_latest_items(channels)

        for channel in channels:
            channel_enum = channel.channel_enum
            channel_conf = channel_enum.conf

            channel_list.append(dict(
                channel_id=channel_enum.value,
                channel_desc=channel_enum.desc,
                id=channel_conf['mch_id'],
                provider=channel_conf['provider'],
                fee=channel.fee,
                fee_type=dict(desc=PaymentFeeTypeEnum(channel.fee_type).desc,
                              value=PaymentFeeTypeEnum(channel.fee_type).value),
                limit_per_min=channel.limit_per_min,
                limit_per_max=channel.limit_per_max,
                limit_day_max=channel.limit_day_max,
                trade_start_time=":".join([str(channel.trade_begin_hour), str(channel.trade_begin_minute)]),
                trade_end_time=":".join([str(channel.trade_end_hour), str(channel.trade_end_minute)]),
                main_time=dict(maintain_begin=channel.maintain_begin if channel.maintain_begin else None,
                               maintain_end=channel.maintain_end if channel.maintain_begin else None),
                state=dict(
                    desc=channel.state.desc,
                    value=channel.state.value
                ),
                reason=channel.get_reason_desc(),
                banks=[bank.value for bank in channel.banks]
            ))

        channel_list = sorted(channel_list, key=lambda item: item['state']['value'])

        data = dict(counts=len(channel_list), withdraws=channel_list)

        return WithdrawListResult(bs_data=data).as_response()


#######################
# 引导规则
#######################
@ns.route('/router/list')
@ResponseDoc.response(ns, api)
class RuleList(Resource):
    method_decorators = admin_decorators

    @ns.marshal_with(RuleListResult.gen_doc(api), as_list=True)
    def post(self):
        """
        引导规则列表
        :return:
        """
        rule_list = []

        rules = ChannelRouter.query_all()

        for rule in rules:
            rule_dict = dict(
                router_id=rule.router_id,
                interface=dict(name=rule.interface.name, desc=rule.interface.desc) if rule.interface else dict(),
                amount_min=rule.amount_min,
                amount_max=rule.amount_max,
                create_time=rule.str_create_time,
                merchants=rule.list_merchants,
                uid_list=rule.uid_list,
                config_list=rule.dict_config_list,
            )
            rule_list.append(rule_dict)

        data = dict(counts=len(rule_list), rules=rule_list)
        return RuleListResult(bs_data=data).as_response()


@ns.route('/router/create')
@ResponseDoc.response(ns, api)
class ChannelRouterAdd(Resource):
    method_decorators = admin_decorators

    @ns.expect(RuleAddList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        新增引导规则
        :return:
        """
        form, error = ChannelRouterAddForm().request_validate()
        if error:
            return error.as_response()

        if form.amount_min.data > form.amount_max.data:
            return DataStartMoreThanError(message="最小金额不能大于最大金额").as_response()

        try:
            ChannelRouter.create_rule(
                config_list=form.config_list.data,
                interface=form.interface.data,
                amount_min=form.amount_min.data,
                amount_max=form.amount_max.data,
                merchants=form.merchants.data,
                uid_list=form.uid_list.data,
            )
        except IntegrityError as e:
            return ChannelSqlIntegrityError(message=str(e)).as_response()

        return ResponseSuccess().as_response()


@ns.route('/router/update')
@ResponseDoc.response(ns, api)
class ChannelRouterUpdate(Resource):
    method_decorators = admin_decorators

    @ns.expect(RuleEditList)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        编辑引导规则
        :return:
        """
        form, error = ChannelRouterUpdateForm().request_validate()
        if error:
            return error.as_response()

        if form.amount_min.data > form.amount_max.data:
            return DataStartMoreThanError(message="最小金额不能大于最大金额").as_response()

        try:
            model, error = ChannelRouter.update_rule(
                router_id=form.router_id.data,
                config_list=form.config_list.data,
                interface=form.interface.data,
                amount_min=form.amount_min.data,
                amount_max=form.amount_max.data,
                merchants=form.merchants.data,
                uid_list=form.uid_list.data,
            )
            if error:
                return DataStartMoreThanError(message=error).as_response()
        except IntegrityError as e:
            return ChannelSqlIntegrityError(message=str(e)).as_response()

        return ResponseSuccess().as_response()


@ns.route('/router2/update')
@ResponseDoc.response(ns, api)
class ChannelRouter2Update(Resource):
    method_decorators = admin_decorators

    @ns.expect(RouterAddDoc)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        编辑通道适用规则
        :return:
        """
        form, error = ChannelRouter2AddForm().request_validate()
        if error:
            return error.as_response()

        current_app.logger.info(form.get_data())

        if form.amount_min.data > form.amount_max.data:
            return DataStartMoreThanError(message="最小金额不能大于最大金额").as_response()

        try:
            model, error = ChannelRouter2.update_router(
                channel_enum=form.channel.data,
                interface=form.interface.data,
                amount_min=form.amount_min.data,
                amount_max=form.amount_max.data,
                merchants=form.merchants.data,
                uid_list=form.uid_list.data,
            )
            if error:
                return DataStartMoreThanError(message=error).as_response()
        except IntegrityError as e:
            return ChannelSqlIntegrityError(message=str(e)).as_response()

        return ResponseSuccess().as_response()
