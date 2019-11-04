import hashlib
from collections import defaultdict

from flask import g
from flask_restplus import Resource

from app.enums.channel import ChannelConfigEnum
from app.forms.backoffice.balance_from import MerchantBalanceEditForm
from app.libs.error_code import MerchantUpdateError, ParameterException

from app.docs.doc_internal.merchant import MerchantListResult, MerchantFeeAdd, ResponseSuccess, MerchantFeeEdit, \
    MerchantBalanceEdit, MerchantConfigResult
from app.libs.doc_response import ResponseDoc
from app.extensions import limiter
from app.enums.trade import PayMethodEnum, PayTypeEnum, OrderSourceEnum, DeliverTypeEnum, PaymentTypeEnum
from app.extensions.ext_api import api_backoffice as api
from app.libs.order_kit import OrderUtils
from app.logics.token.admin_token import admin_decorators
from app.models.merchant import MerchantInfo, MerchantFeeConfig, MerchantBalanceEvent
from config import MerchantEnum, MerchantDomainConfig
from app.forms.backoffice.merchant import EditMerchantRateForm, MerchantFeeAddForm
from app.libs.error_code import SqlIntegrityError

ns = api.namespace('merchant', description='商户管理')


@ns.route('/list')
@ResponseDoc.response(ns, api)
class MerchantList(Resource):
    method_decorators = admin_decorators

    @ns.marshal_with(MerchantListResult.gen_doc(api), as_list=True)
    def post(self):
        """
        商户列表
        :return:
        """
        merchant_list = list()

        merchants = MerchantInfo.query_all()

        all_configs = MerchantFeeConfig.query_all()
        all_configs = MerchantFeeConfig.filter_latest_items(all_configs)

        merchant_all_configs = defaultdict(list)
        for fee in all_configs:
            merchant_all_configs[fee.merchant].append(fee)

        for merchant in merchants:
            fee_configs = merchant_all_configs.get(merchant.merchant)
            if not fee_configs:
                continue

            withdraw_fees = [x for x in fee_configs if x.payment_way == PayTypeEnum.WITHDRAW]
            recharge_fees = [x for x in fee_configs if x.payment_way == PayTypeEnum.DEPOSIT]

            withdraw_desc = ''
            cost_type = None
            if withdraw_fees:
                withdraw_desc = withdraw_fees[0].value_description
                cost_type = withdraw_fees[0].cost_type.name

            merchant_list.append(dict(
                id=merchant.id,
                name=merchant.merchant.name,
                balance_total=merchant.balance_total,
                balance_available=merchant.balance_available,
                balance_income=merchant.balance_income,
                balance_frozen=merchant.balance_frozen,
                type=merchant.m_type.name,
                domains='\n'.join(MerchantDomainConfig.get_domains(merchant.merchant)),
                state=merchant.state.name,
                channel_fees=dict(
                    withdraw=withdraw_desc,
                    cost_type=cost_type,
                    deposit=[
                        dict(
                            desc=x.payment_method.desc,
                            value=x.payment_method.value,
                            rate=x.value_description,
                        )
                        for x in recharge_fees
                    ]
                )
            ))

        data = dict(counts=len(merchant_list), merchants=merchant_list)

        return MerchantListResult(bs_data=data).as_response()


@ns.route('/config/get')
@ResponseDoc.response(ns, api)
class MerchantConfigGetRes(Resource):
    method_decorators = admin_decorators

    @ns.marshal_with(MerchantConfigResult.gen_doc(api), as_list=True)
    def post(self):
        """
        获取创建商户所需的配置信息
        :return:
        """
        result = dict(
            merchant_names=MerchantEnum.get_name_type_pairs(),
            payment_methods=PayMethodEnum.get_desc_value_pairs(),
            withdraw_type=DeliverTypeEnum.get_desc_value_pairs(),
            channels_withdraw=ChannelConfigEnum.get_withdraw_desc_name_pairs(),
            channels_deposit=ChannelConfigEnum.get_deposit_desc_name_pairs(),
        )
        return MerchantConfigResult(bs_data=result).as_response()


@ns.route('/fee/add')
@ResponseDoc.response(ns, api, [SqlIntegrityError])
class MerchantFeeAddRes(Resource):
    method_decorators = admin_decorators

    @ns.expect(MerchantFeeAdd)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        新建商户 新增费率
        """
        form, error = MerchantFeeAddForm().request_validate()
        if error:
            return error.as_response()

        # 充值费率设置
        for item in form.deposit_info:
            if not isinstance(item.data['value'], str):
                return ParameterException(message="充值费率必须传入字符串类型").as_response()

        # 提现费率
        if not isinstance(form.withdraw_info.data['value'], str):
            return ParameterException(message="提现费率必须传入字符串类型").as_response()

        merchant = form.data['name']

        # 第一步向数据库中插入商户数据
        models = MerchantInfo.create_merchant_models(merchant, form.data['type'])

        # 充值费率设置
        merchant_fee_dict = []
        for item in form.deposit_info:
            merchant_fee_dict.append(dict(
                merchant=merchant,
                payment_way=PayTypeEnum.DEPOSIT,
                value=item.data['value'],
                fee_type=item.data['fee_type'],
                payment_method=item.data['name'],
            ))

        # 提现费率
        merchant_fee_dict.append(dict(
            merchant=merchant,
            payment_way=PayTypeEnum.WITHDRAW,
            value=form.withdraw_info.data['value'],
            fee_type=form.withdraw_info.data['fee_type'],
            cost_type=form.withdraw_info.data['cost_type'],
        ))

        rst, error = MerchantFeeConfig.update_fee_config(merchant, merchant_fee_dict, models)
        if error:
            return error.as_response()

        return ResponseSuccess().as_response()


@ns.route('/fee/edit')
@ResponseDoc.response(ns, api)
class MerchantFeeEditRes(Resource):
    method_decorators = admin_decorators

    @ns.expect(MerchantFeeEdit)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        商户编辑 编辑费率
        """
        # 验证费率表单
        form, error = EditMerchantRateForm().request_validate()
        if error:
            return error.as_response()

        merchant = form.data['name']
        merchant_fee_dict = []

        for item in form.deposit_info:
            merchant_fee_dict.append(dict(
                merchant=merchant,
                payment_way=PayTypeEnum.DEPOSIT,
                value=item.data['value'],
                fee_type=item.data['fee_type'],
                payment_method=item.data['name'],
            ))

        if form.withdraw_info.data['value']:
            merchant_fee_dict.append(dict(
                merchant=merchant,
                payment_way=PayTypeEnum.WITHDRAW,
                value=form.withdraw_info.data['value'],
                fee_type=form.withdraw_info.data['fee_type'],
                cost_type=form.withdraw_info.data['cost_type'],
            ))

        MerchantFeeConfig.update_fee_config(merchant, merchant_fee_dict)

        return ResponseSuccess().as_response()


@ns.route('/balance/edit')
@ResponseDoc.response(ns, api, [MerchantUpdateError, ])
class MerchantBalanceEditRes(Resource):
    method_decorators = admin_decorators

    @ns.expect(MerchantBalanceEdit)
    @ns.marshal_with(ResponseSuccess.gen_doc(api), as_list=True)
    def post(self):
        """
        余额调整
        """
        form, error = MerchantBalanceEditForm.request_validate()
        if error:
            return error.as_response()

        rst, msg = MerchantBalanceEvent.update_balance(
            merchant=form.name.data,
            ref_id=OrderUtils.gen_unique_ref_id(),
            source=OrderSourceEnum.MANUALLY,
            order_type=PayTypeEnum.MANUALLY,
            value=form.amount.data,
            bl_type=form.bl_type.data,
            ad_type=form.ad_type.data,
            tx_id=OrderUtils.gen_normal_tx_id(g.user.uid),
            comment=form.reason.data,
        )

        if rst != 0:
            return MerchantUpdateError(message=msg).as_response()

        return ResponseSuccess().as_response()
