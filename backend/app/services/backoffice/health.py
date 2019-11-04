from decimal import Decimal

import requests
from flask import request, current_app
from flask_restplus import Resource

from app.caches.auth_code import AuthCodeLimiterCache
from app.caches.limiter import Limiter
from app.caches.user_flag import UserFlagCache
from app.caches.user_password import UserPasswordLimitCache, UserPasswordCache
from app.constants.admin_ip import ADMIN_IP_WHITE_LIST
from app.enums.account import AccountFlagEnum, UserPermissionEnum
from app.enums.trade import PayTypeEnum, InterfaceTypeEnum
from app.extensions import limiter, db
from app.libs.csv_kit import CsvKit
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.libs.decorators import check_ip_in_white_list
from app.libs.error_code import ResponseSuccess, MerchantConfigWithdrawError, MerchantConfigDepositError
from app.libs.order_kit import OrderUtils
from app.libs.string_kit import PhoneNumberParser
from app.logics.channel.chanel_cache import ChannelLimitCacheCtl
from app.logics.channel.channel_list import ChannelListHelper
from app.logics.mobile.auth_code import AuthCodeLimiter
from app.models.backoffice.admin_log import AdminLog
from app.models.backoffice.admin_user import AdminUser
from app.models.balance import UserBalanceEvent, UserBalance
from app.models.channel import ChannelConfig
from app.models.merchant import MerchantBalanceEvent, MerchantInfo, MerchantFeeConfig
from app.models.order.order import OrderDeposit, OrderWithdraw
from app.models.order.order_blobal import OrderConstraint
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw
from app.models.order.order_event import OrderEvent
from app.models.user import User, UserBindInfo
from config import MerchantEnum, MerchantDomainConfig
from . import api

ns = api.namespace('health', description='接口联通性测试')

DEBUG_LOG = False
method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]


@ns.route('/check')
class HealthCheck(Resource):

    def get(self):
        """
        联通性测试
        :return:
        """
        return 'ok'


@ns.route('/celery/add')
class TaskAdd(Resource):
    def get(self):
        """
        联通性测试
        :return:
        """
        from app.services.celery.order import task_add_together
        rst = task_add_together.delay(1, 2)
        return rst.result


@ns.route('/rate/limit/check')
class RateLimitCheck(Resource):
    method_decorators = [limiter.limit("1/second")]

    def get(self):
        """
        限速测试
        :return:
        """
        return 'ok'


@ns.route('/register/admin')
class RegisterAdminUser(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        联通性测试
        :return:
        """
        from scripts.admin_user import init_admin_user

        if not request.args:
            return ResponseSuccess(message="参数规则：?account=panda").as_response()

        try:
            account = request.args['account']
        except:
            return ResponseSuccess(message="请输入admin账号名称").as_response()

        account, password = init_admin_user(account, None)

        return ResponseSuccess(bs_data=dict(
            account=account,
            password=password
        )).as_response()


@ns.route('/register/merchant')
class RegisterMerchantUser(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        联通性测试
        :return:
        """
        from scripts.admin_user import init_merchant_user

        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=TEST").as_response()

        try:
            account = request.args['merchant']
        except:
            return ResponseSuccess(message="请输入商户分配的账号名称").as_response()

        try:
            merchant = MerchantEnum.from_name(account)
        except:
            return ResponseSuccess(message="请输入有效的商户名称").as_response()

        account, password = init_merchant_user(merchant.value, merchant.name, None)
        return ResponseSuccess(bs_data=dict(
            account=account,
            password=password
        )).as_response()


@ns.route('/query/user/balance')
class QueryUserBalance(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询用户余额
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?account=8613812349999&merchant=test").as_response()

        try:
            account = request.args.get('account')
            if account:
                account = '+' + account.strip('+').strip()
                if not PhoneNumberParser.is_valid_number(account):
                    raise
            else:
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        user = User.query_user(merchant, account=account)
        if not user:
            return ResponseSuccess(message="手机号码未注册, account: %s" % account).as_response()

        user_balance = UserBalance.query_balance(user.uid, merchant).first()

        return ResponseSuccess(bs_data=dict(
            account=account,
            uid=user.uid,
            balance=str(user_balance.real_balance),
        )).as_response()


@ns.route('/alter/balance')
class AlterUserBalance(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        联通性测试
        :return:
        """
        from scripts.user_balance import add_user_balance

        if not (current_app.config['DEBUG'] or current_app.config['TESTING']):
            return ResponseSuccess(message="无权限访问")

        if not request.args:
            return ResponseSuccess(message="参数规则：?account=8613812349999&balance=100").as_response()

        try:
            account = '+' + request.args['account'].strip('+').strip()
            if not PhoneNumberParser.is_valid_number(account):
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        try:
            balance = Decimal(request.args['balance'])
        except:
            return ResponseSuccess(message="无效的余额").as_response()

        total, msg = add_user_balance(account, balance, register=False)
        if msg:
            return ResponseSuccess(message=msg).as_response()

        return ResponseSuccess(bs_data=dict(
            account=account,
            delta=str(balance),
            total=str(total),
        )).as_response()


@ns.route('/merchant/balance/events')
class QueryMerchantBalanceEvents(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询商户余额变更流水
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&date=20190901&export=1").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
            merchant_info = MerchantInfo.query_merchant(merchant)
            if not merchant_info:
                raise
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            date = request.args.get('date')
            if date:
                date = DateTimeKit.str_to_datetime(date, DateTimeFormatEnum.TIGHT_DAY_FORMAT, to_date=True)
            else:
                date = DateTimeKit.get_cur_date()
        except:
            return ResponseSuccess(message="请输入有效的查询日期，格式为：20190901").as_response()

        balance = dict(
            balance_total=str(merchant_info.balance_total),
            balance_available=str(merchant_info.balance_available),
            balance_income=str(merchant_info.balance_income),
            balance_frozen=str(merchant_info.balance_frozen),
        )

        events = MerchantBalanceEvent.query_by_date(date, merchant=merchant, date=date)

        rst = dict(
            data=list(),
            sum_value=0,
            balance=balance,
        )

        rst['sql'] = str(events)

        for event in events:
            rst['sum_value'] += event.value_real
            rst['data'].append(dict(
                create_time=event.create_time,
                ref_id=event.ref_id,
                order_type=event.order_type.desc,
                source=event.source.desc,
                bl_type=event.bl_type.desc,
                value=str(event.value_real),
                ad_type=event.ad_type.desc,
                tx_id=event.tx_id,
                comment=event.comment,
            ))

        rst['data'] = sorted(rst['data'], key=lambda x: x['create_time'], reverse=True)
        for x in rst['data']:
            x['create_time'] = DateTimeKit.datetime_to_str(x['create_time'])

        if rst['data'] and request.args.get('export'):
            filename = 'merchant_balance_events_%s.csv' % DateTimeKit.datetime_to_str(
                date,
                DateTimeFormatEnum.TIGHT_DAY_FORMAT
            )
            return CsvKit.send_csv(rst['data'], filename=filename, fields=rst['data'][0].keys())

        rst['sum_value'] = str(rst['sum_value'])

        return ResponseSuccess(bs_data=rst).as_response()


@ns.route('/user/balance/events')
class QueryUserBalanceEvents(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询用户余额变更流水
        :return:
        """
        if not request.args:
            return ResponseSuccess(
                message="参数规则：?merchant=test&account=8618912341234&date=20190901&export=1").as_response()

        try:
            account = request.args.get('account')
            if account:
                account = '+' + account.strip('+').strip()
                if not PhoneNumberParser.is_valid_number(account):
                    raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            date = request.args.get('date')
            if date:
                date = DateTimeKit.str_to_datetime(date, DateTimeFormatEnum.TIGHT_DAY_FORMAT, to_date=True)
            else:
                date = DateTimeKit.get_cur_date()
        except:
            return ResponseSuccess(message="请输入有效的查询日期，格式为：20190901").as_response()

        rst = dict(
            data=list(),
            sum_value=0,
        )

        events = UserBalanceEvent.query_by_date(date, merchant=merchant, date=date)
        if account:
            user = User.query_user(merchant, account=account)
            if not user:
                return ResponseSuccess(message="用户不存在，请检查参数。商户：%s，手机号码：%s" % (merchant.name, account))

            user_balance = UserBalance.query_balance(user.uid, merchant).first()
            rst.update(user=dict(
                account=user.account,
                uid=user.uid,
                user_balance=str(user_balance.real_balance),
            ))
            events = events.filter_by(uid=user.uid)

        rst['sql'] = str(events)
        for event in events:
            rst['sum_value'] += event.value_real
            rst['data'].append(dict(
                create_time=event.create_time,
                uid=event.uid,
                ref_id=event.ref_id,
                order_type=event.order_type.desc,
                source=event.source.desc,
                bl_type=event.bl_type.desc,
                value=str(event.value_real),
                ad_type=event.ad_type.desc,
                tx_id=event.tx_id,  # 大整数，转为字符串
                comment=event.comment,
                extra=event.raw_extra,
            ))

        rst['data'] = sorted(rst['data'], key=lambda x: x['create_time'], reverse=True)
        for x in rst['data']:
            x['create_time'] = DateTimeKit.datetime_to_str(x['create_time'])

        if rst['data'] and request.args.get('export'):
            filename = 'user_balance_events_%s.csv' % DateTimeKit.datetime_to_str(
                date,
                DateTimeFormatEnum.TIGHT_DAY_FORMAT
            )
            return CsvKit.send_csv(rst['data'], filename=filename, fields=rst['data'][0].keys())

        rst['sum_value'] = str(rst['sum_value'])

        return ResponseSuccess(bs_data=rst).as_response()


@ns.route('/admin/log')
class QueryAdminLog(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        后台管理员操作日志
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?account=panda&date=20190901&export=1").as_response()

        account = request.args['account']
        if account:
            user = AdminUser.query_user(account=account)
            if not user:
                return ResponseSuccess(message="用户不存在，请检查参数。account：%s" % account).as_response()

        try:
            date = request.args.get('date')
            if date:
                date = DateTimeKit.str_to_datetime(date, DateTimeFormatEnum.TIGHT_DAY_FORMAT, to_date=True)
            else:
                date = DateTimeKit.get_cur_date()
        except:
            return ResponseSuccess(message="请输入有效的查询日期，格式为：20190901").as_response()

        events = AdminLog.query_by_date(date)
        if account:
            events = events.filter_by(account=account)

        rst = list()

        for event in events:
            rst.append(dict(
                create_time=event.create_time,
                account=event.account,
                url=event.url,
                ip=event.ip,
                module=event.module.desc,
                model=event.model,
                model_id=event.model_id,
                data_before=event.data_before,
                data_after=event.data_after,
            ))

        rst = sorted(rst, key=lambda x: x['create_time'], reverse=True)
        for x in rst:
            x['create_time'] = DateTimeKit.datetime_to_str(x['create_time'])

        if rst and request.args.get('export'):
            filename = 'admin_log_%s.csv' % DateTimeKit.datetime_to_str(
                date,
                DateTimeFormatEnum.TIGHT_DAY_FORMAT
            )
            return CsvKit.send_csv(rst, filename=filename, fields=rst[0].keys())

        return ResponseSuccess(bs_data=rst).as_response()


@ns.route('/order/events', endpoint="health_order_events_query")
class QueryOrderEvents(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        订单修改日志
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&date=20190901&order_id=123&uid=123&ref_id=xxx&export=1，"
                                           "必填参数：merchant，"
                                           "可选参数：date，order_id，uid，ref_id，export，"
                                           "当不填写date时，默认查询当天所有的数据").as_response()

        try:
            date = request.args.get('date')
            if date:
                date = DateTimeKit.str_to_datetime(date, DateTimeFormatEnum.TIGHT_DAY_FORMAT, to_date=True)
            else:
                date = DateTimeKit.get_cur_date()
        except:
            return ResponseSuccess(message="请输入有效的查询日期，格式为：20190901").as_response()

        q_params = dict()
        order_id = request.args.get('order_id')
        try:
            order_id = OrderUtils.parse_tx_id(order_id)
        except:
            pass
        if order_id:
            q_params['order_id'] = order_id
        uid = request.args.get('uid')
        if uid:
            q_params['uid'] = uid
        ref_id = request.args.get('ref_id')
        if ref_id:
            q_params['ref_id'] = ref_id
        if not q_params:
            return ResponseSuccess(message="必须输入 order_id/uid/ref_id 其中一个或多个参数").as_response()

        events = OrderEvent.query_model(query_fields=q_params, date=date)

        rst = list()

        for event in events:
            rst.append(dict(
                create_time=event.create_time,
                order_id=event.order_id,
                uid=event.uid,
                ref_id=event.ref_id,
                data_before=event.data_before,
                data_after=event.data_after,
            ))

        rst = sorted(rst, key=lambda x: x['create_time'], reverse=True)
        for x in rst:
            x['create_time'] = DateTimeKit.datetime_to_str(x['create_time'])

        if rst and request.args.get('export'):
            filename = 'order_events_%s.csv' % DateTimeKit.datetime_to_str(
                date,
                DateTimeFormatEnum.TIGHT_DAY_FORMAT
            )
            return CsvKit.send_csv(rst, filename=filename, fields=rst[0].keys())

        return ResponseSuccess(bs_data=rst).as_response()


@ns.route('/hot/table/check')
class HotTableCheck(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        检查热表数据
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&date=20190901").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            date = request.args.get('date')
            if date:
                date = DateTimeKit.str_to_datetime(date, DateTimeFormatEnum.TIGHT_DAY_FORMAT, to_date=True)
            else:
                date = DateTimeKit.get_cur_date()
        except:
            return ResponseSuccess(message="请输入有效的查询日期，格式为：20190901").as_response()

        kwargs = dict(
            date=date,
            merchant=merchant,
            only_hot=request.args.get('only_hot'),
            only_cold=request.args.get('only_cold'),
        )

        rst = dict(
            OrderDeposit=OrderDeposit.query_by_date(date, **kwargs).count(),
            OrderWithdraw=OrderWithdraw.query_by_date(date, **kwargs).count(),
            OrderDetailDeposit=OrderDetailDeposit.query_by_date(date, **kwargs).count(),
            OrderDetailWithdraw=OrderDetailWithdraw.query_by_date(date, **kwargs).count(),
        )
        kwargs['merchant'] = merchant.name
        kwargs['date'] = DateTimeKit.datetime_to_str(date)
        rst['kwargs'] = kwargs

        return ResponseSuccess(bs_data=rst).as_response()


@ns.route('/deposit/channel/choice')
class ChannelChoice(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询可用的通道
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&interface=&amount=&uid=").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(
                message="请输入正确的 merchant，有效的 merchant 包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            interface = request.args.get('interface')
            if interface:
                interface = InterfaceTypeEnum.from_name(interface)
        except:
            return ResponseSuccess(
                message="请输入正确的 interface，有效的 interface 包括：%s" % InterfaceTypeEnum.get_names()).as_response()

        try:
            amount = request.args.get('amount') or 0
            if amount:
                amount = Decimal(amount)
        except:
            return ResponseSuccess(message="请输入正确的 amount")

        try:
            uid = request.args.get('uid')
            if uid:
                uid = int(uid)
        except:
            return ResponseSuccess(message="请输入正确的 uid")

        routers = ChannelListHelper.get_channel_payment_type_router(
            interface=interface,
            amount=amount,
            merchant=merchant,
            uid=uid,
        )
        channels = ChannelListHelper.get_available_channels(merchant, PayTypeEnum.DEPOSIT)
        payment_type_list = ChannelListHelper.choice_one_channel_for_payment_type(channels, routers, merchant, amount)

        for item in payment_type_list:
            item['limit_min'] = str(item['limit_min'])
            item['limit_max'] = str(item['limit_max'])

        return ResponseSuccess(bs_data=payment_type_list).as_response()


@ns.route('/deposit/order')
class QueryDepositOrder(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询可用的通道
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?tx_id=xxxx，交易ID，必填").as_response()

        try:
            tx_id = request.args['tx_id']
        except:
            return ResponseSuccess(message="必填交易ID").as_response()

        order = OrderDeposit.query_by_tx_id(tx_id)
        if not order:
            return ResponseSuccess(message="订单不存在，请确认交易号是否正确: %s" % tx_id).as_response()

        order_detail = OrderDetailDeposit.query_by_tx_id(tx_id)

        channel = ChannelConfig.query_by_channel_id(order.channel_id)
        fee_config = MerchantFeeConfig.query_by_config_id(order.mch_fee_id)

        order_info = dict(
            order_id=order.order_id,
            create_time=order.str_create_time,
            uid=order.uid,
            sys_tx_id=order.sys_tx_id,
            mch_tx_id=order.mch_tx_id,
            channel_tx_id=order.channel_tx_id,
            amount=str(order.amount),
            tx_amount=str(order.tx_amount),
            source=order.source.desc,
            pay_method=order.pay_method.desc,
            state=order.state.desc,
            settle=order.settle.desc,
            deliver=order.deliver.desc,
            channel_id=order.channel_id,
            channel=channel.short_description,
            mch_fee_id=order.mch_fee_id,
            mch_fee=fee_config.short_description,
            in_type=order_detail.in_type.desc,
            offer=str(order_detail.offer),
            fee=str(order_detail.fee),
            cost=str(order_detail.cost),
            profit=str(order_detail.profit),
            ip=order_detail.ip,
        )

        return ResponseSuccess(bs_data=order_info).as_response()


@ns.route('/update/channel/limit/cache')
class QueryDepositOrder(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        更新通道缓存
        :return:
        """
        # ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).sync_db_channels_to_cache()
        # ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).sync_db_channels_to_cache()

        return ResponseSuccess(bs_data=dict(
            # depost=list(map(str, ChannelLimitCacheCtl(PayTypeEnum.DEPOSIT).get_channel_limit())),
            # withdraw=list(map(str, ChannelLimitCacheCtl(PayTypeEnum.WITHDRAW).get_channel_limit())),
        )).as_response()


@ns.route('/http/proxy/check')
class QueryDepositOrder(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        测试外网访问，正向代理是否正常
        :return:
        """
        test_url = 'https://google.com'
        rst = requests.get(test_url)
        return ResponseSuccess(bs_data=dict(
            status_code=rst.status_code,
            test_url=test_url,
        )).as_response()


@ns.route('/auth/code/check')
class AuthCodeCheck(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询短信验证码
        :return:
        """
        try:
            account = request.args.get('account')
            if account:
                account = '+' + account.strip('+').strip()
                if not PhoneNumberParser.is_valid_number(account):
                    raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        accounts = list()
        if account:
            accounts.append(account)
        else:
            for key in AuthCodeLimiterCache.scan_iter(AuthCodeLimiterCache.KEY_PREFIX):
                accounts.append(AuthCodeLimiterCache.split_key(key=key.decode('utf8'))[-1])

        codes = list()
        for account in accounts:
            cache = AuthCodeLimiter(account)
            codes.append(dict(
                account=account,
                sent_times=cache.get_times(),
                is_limited=cache.is_limited(),
                ttl=cache.cache.get_ttl(),
            ))

        return ResponseSuccess(bs_data=codes).as_response()


@ns.route('/auth/code/clear')
class AuthCodeClear(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        删除某个手机号码的短信发送次数限制
        :return:
        """
        try:
            account = request.args.get('account')
            if account:
                account = '+' + account.strip('+').strip()
                if not PhoneNumberParser.is_valid_number(account):
                    raise
            else:
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        AuthCodeLimiter(account).cache.delete()

        accounts = list()
        for key in AuthCodeLimiterCache.scan_iter(AuthCodeLimiterCache.KEY_PREFIX):
            accounts.append(AuthCodeLimiterCache.split_key(key=key.decode('utf8'))[-1])

        if account in accounts:
            return ResponseSuccess(message="删除失败，accounts: %s" % accounts).as_response()

        codes = list()
        for account in accounts:
            cache = AuthCodeLimiter(account)
            codes.append(dict(
                account=account,
                sent_times=cache.get_times(),
                is_limited=cache.is_limited(),
                ttl=cache.cache.get_ttl(),
            ))

        return ResponseSuccess(message="删除成功", bs_data=dict(
            codes=codes,
        )).as_response()


@ns.route('/revoke/ref/id')
class RevokeRefId(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        测试外网访问，正向代理是否正常
        :return:
        """
        try:
            tx_id = request.args['tx_id']
        except:
            return ResponseSuccess(message="必填交易ID").as_response()

        order = OrderDeposit.query_by_tx_id(tx_id)
        if not order:
            return ResponseSuccess(message="订单不存在，请确认交易号是否正确: %s" % tx_id).as_response()

        state_before = OrderConstraint.query_by_order_id(order.order_id).state

        with db.auto_commit():
            OrderConstraint.revoke_order_state(order.order_id, order.state)

        state_after = OrderConstraint.query_by_order_id(order.order_id).state

        return ResponseSuccess(bs_data=dict(
            order_id=order.order_id,
            sys_tx_id=order.sys_tx_id,
            order_state=order.state.desc,
            state_before=state_before.desc,
            state_after=state_after.desc,
        )).as_response()


@ns.route('/password/error/check')
class PasswordErrorCheck(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        查询密码错误限制
        :return:
        """
        try:
            account = request.args.get('account')
            if account:
                account = '+' + account.strip('+').strip()
                if not PhoneNumberParser.is_valid_number(account):
                    raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        accounts = list()
        if account:
            accounts.append(account)
        else:
            for key in UserPasswordCache.scan_iter(UserPasswordCache.KEY_PREFIX):
                accounts.append(UserPasswordCache.split_key(key=key.decode('utf8'))[-1])

        codes = list()
        for account in accounts:
            cache = UserPasswordLimitCache(account)
            codes.append(dict(
                account=account,
                sent_times=cache.get_times(),
                is_limited=cache.is_limited(),
                ttl=cache.cache.get_ttl(),
            ))

        return ResponseSuccess(bs_data=codes).as_response()


@ns.route('/password/error/clear')
class PasswordErrorClear(Resource):
    method_decorators = method_decorators

    def get(self):
        """
        删除某个手机号码的密码错误次数限制
        :return:
        """
        try:
            account = request.args.get('account')
            if account:
                account = '+' + account.strip('+').strip()
                if not PhoneNumberParser.is_valid_number(account):
                    raise
            else:
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        UserPasswordLimitCache(account).cache.delete()

        accounts = list()
        for key in UserPasswordCache.scan_iter(UserPasswordCache.KEY_PREFIX):
            accounts.append(UserPasswordCache.split_key(key=key.decode('utf8'))[-1])

        if account in accounts:
            return ResponseSuccess(message="删除失败，accounts: %s" % accounts).as_response()

        codes = list()
        for account in accounts:
            cache = UserPasswordLimitCache(account)
            codes.append(dict(
                account=account,
                sent_times=cache.get_times(),
                is_limited=cache.is_limited(),
                ttl=cache.cache.get_ttl(),
            ))

        return ResponseSuccess(message="删除成功", bs_data=dict(
            codes=codes,
        )).as_response()


@ns.route('/merchant/check')
class DomainCheck(Resource):
    method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]

    def get(self):
        """
        商户配置查询
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        merchant_info = MerchantInfo.query_merchant(merchant)
        if not merchant_info:
            return ResponseSuccess(message="未创建商户").as_response()

        bs_data = dict(
            balance=dict(
                balance_total=str(merchant_info.balance_total),
                balance_available=str(merchant_info.balance_available),
                balance_income=str(merchant_info.balance_income),
                balance_frozen=str(merchant_info.balance_frozen),
            ),
            merchant=merchant.name,
            domains=MerchantDomainConfig.get_domains(merchant),
            # db=DBEnum(merchant.name).get_db_name(),
        )

        deposit_fees = MerchantFeeConfig.query_active_configs(query_fields=dict(
            merchant=merchant,
            payment_way=PayTypeEnum.DEPOSIT,
        ))
        deposit_fees = MerchantFeeConfig.filter_latest_items(deposit_fees)
        if not deposit_fees:
            return MerchantConfigDepositError(bs_data=bs_data).as_response()
        bs_data['deposit_fees'] = [x.short_description for x in deposit_fees]

        withdraw_fees = MerchantFeeConfig.query_latest_one(query_fields=dict(
            merchant=merchant,
            payment_way=PayTypeEnum.WITHDRAW,
        ))
        if not withdraw_fees:
            return MerchantConfigWithdrawError(bs_data=bs_data).as_response()
        bs_data['withdraw_fees'] = withdraw_fees.short_description

        channels = ChannelListHelper.get_available_channels(merchant, PayTypeEnum.DEPOSIT)
        bs_data['deposit_channels'] = [x.short_description for x in channels]

        channels = ChannelListHelper.get_available_channels(merchant, PayTypeEnum.WITHDRAW)
        bs_data['withdraw_channels'] = [x.short_description for x in channels]

        return ResponseSuccess(bs_data=bs_data).as_response()


@ns.route('/channel/check')
class DomainCheck(Resource):
    method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]

    def get(self):
        """
        通道配置查询
        :return:
        """
        deposit_channels = ChannelListHelper.get_config_channels(PayTypeEnum.DEPOSIT)
        withdraw_channels = ChannelListHelper.get_config_channels(PayTypeEnum.WITHDRAW)

        bs_data = dict(
            deposit_channels=[x.short_description for x in deposit_channels],
            withdraw_channels=[x.short_description for x in withdraw_channels],
        )
        return ResponseSuccess(bs_data=bs_data).as_response()


@ns.route('/user/bind')
class UserBindResource(Resource):
    method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]

    def get(self):
        """
        给用户绑定信息
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&account=861891111&name=大王&unbind=").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            account = request.args['account']
            account = '+' + account.strip('+').strip()
            if not PhoneNumberParser.is_valid_number(account):
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        try:
            name = request.args['name']
        except:
            return ResponseSuccess(message="绑定名称必填").as_response()

        user = User.query_user(merchant, account=account)
        if not user:
            return ResponseSuccess(message="手机号码未注册").as_response()

        bind_info = UserBindInfo.query_bind_by_uid(user.uid)

        if request.args.get('unbind'):
            if not bind_info:
                return ResponseSuccess(message="未绑定任何别名，无需解绑").as_response()

            if UserBindInfo.unbind_account(user.uid):
                return ResponseSuccess(message="解绑成功").as_response()
            else:
                return ResponseSuccess(message="解绑失败").as_response()
        else:
            if not bind_info:
                if UserBindInfo.bind_account(user.uid, merchant, account=user.account, name=name):
                    msg = "绑定成功"
                else:
                    msg = "绑定失败"
                    return ResponseSuccess(message=msg).as_response()
            else:
                msg = "无需重复绑定，已经绑定名称：%s" % bind_info.name

            bind_info = UserBindInfo.query_bind_by_uid(user.uid)
            bs_data = dict(
                name=bind_info.name,
                account=bind_info.account,
                uid=user.uid,
            )
            return ResponseSuccess(bs_data=bs_data, message=msg).as_response()


@ns.route('/user/flag/update')
class UserFlagResource(Resource):
    method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]

    def get(self):
        """
        给用户绑定信息
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&account=861891111&flag=VIP").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            account = request.args['account']
            account = '+' + account.strip('+').strip()
            if not PhoneNumberParser.is_valid_number(account):
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        try:
            flag = AccountFlagEnum.from_name(request.args['flag'])
        except:
            return ResponseSuccess(message="标签错误，有效的标签包括: %s" % AccountFlagEnum.get_name_list()).as_response()

        user = User.query_user(merchant, account=account)
        if not user:
            return ResponseSuccess(message="手机号码未注册").as_response()

        User.update_user_flag(merchant, flag, account=account)
        user = User.query_user(merchant, account=account)

        bs_data = dict(
            account=account,
            uid=user.uid,
            flag=user.flag.desc,
            is_auth=user.is_official_auth,
            cache_flag=UserFlagCache(user.uid).get_flag().name,
        )
        return ResponseSuccess(bs_data=bs_data).as_response()


@ns.route('/user/permission/update')
class UserFlagResource(Resource):
    method_decorators = [check_ip_in_white_list(ADMIN_IP_WHITE_LIST), limiter.limit("1/second")]

    def get(self):
        """
        给用户绑定信息
        :return:
        """
        if not request.args:
            return ResponseSuccess(message="参数规则：?merchant=test&account=861891111&perm=DEPOSIT|BINDCARD").as_response()

        try:
            merchant = MerchantEnum.from_name(request.args['merchant'])
        except:
            return ResponseSuccess(message="请输入正确的商户名称，有效的商户名称包括：%s" % MerchantEnum.get_names()).as_response()

        try:
            account = request.args['account']
            account = '+' + account.strip('+').strip()
            if not PhoneNumberParser.is_valid_number(account):
                raise
        except:
            return ResponseSuccess(message="请输入正确的用户手机号码，必须有完整区号，不填+号，如：8613812349999").as_response()

        try:
            perms = request.args['perm'].split('|')
            perms = [UserPermissionEnum.from_name(perm) for perm in perms]
        except:
            return ResponseSuccess(message="标签权限，有效的权限包括: %s" % UserPermissionEnum.get_name_list()).as_response()

        user = User.query_user(merchant, account=account)
        if not user:
            return ResponseSuccess(message="手机号码未注册").as_response()

        User.update_user_permission(merchant, perms, account=account)
        user = User.query_user(merchant, account=account)

        bs_data = dict(
            account=account,
            uid=user.uid,
            perms=user.permission_names,
        )
        return ResponseSuccess(bs_data=bs_data).as_response()
