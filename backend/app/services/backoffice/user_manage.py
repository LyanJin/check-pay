from decimal import Decimal

from app.docs.doc_internal.user_manage import UserList, UserListResult, UserInfo, UserBalanceEditApi, \
    UserEntriesDetailResult, UserDepositResult, UserTransaction, UserBankInfo
from app.enums.trade import BalanceAdjustTypeEnum, OrderSourceEnum, BalanceTypeEnum, PayTypeEnum, OrderStateEnum, \
    PaymentBankEnum
from app.extensions.ext_api import api_backoffice as api
from app.forms.backoffice.user_manage import UserListSelectForm, UserInfoForm, UserBalanceEditForm, UserTransactionForm, \
    UserBankDeleteForm
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit
from app.libs.doc_response import ResponseDoc

from flask_restplus import Resource

from app.libs.error_code import ResponseSuccess, AdjustUserBalanceError, NoSourceError, UserBalanceNoFoundError
from app.libs.string_kit import PhoneNumberParser
from app.logics.pagination.paginate_list import Pagination
from app.logics.token.admin_token import admin_decorators
from app.logics.transaction.adjust_ctl import AdjustTransactionCtl
from app.models.balance import UserBalance
from app.models.bankcard import BankCard
from app.models.merchant import MerchantBalanceEvent, MerchantInfo
from app.models.order.order import OrderDeposit, OrderWithdraw
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw
from app.models.user import User, GlobalUid

ns = api.namespace('user_manage', description='用户管理')


@ns.route("/user/list")
@ResponseDoc.response(ns, api)
class UserManageList(Resource):
    method_decorators = admin_decorators

    @ns.expect(UserList)
    @ns.marshal_with(UserListResult.gen_doc(api), as_list=True)
    def post(self):

        """
        用户列表
        :return:
        """
        form, error = UserListSelectForm.request_validate()
        if error:
            return error.as_response()

        kwargs = dict()
        if form.phone_number.data:
            phone_number = str(form.phone_number.data)
            if phone_number.find("+") < 0:
                phone_number = "{}{}".format("+", phone_number)
            kwargs['account'] = phone_number

        user_query = User.query.filter_by(**kwargs)
        if form.start_datetime.data:
            user_query = user_query.filter(
                User._create_time >= DateTimeKit.datetime_to_timestamp(form.start_datetime.data))
        if form.end_datetime.data:
            user_query = user_query.filter(
                User._create_time <= DateTimeKit.datetime_to_timestamp(form.end_datetime.data))
        paginate = user_query.paginate(
            form.page_index.data, form.page_size.data, False)

        total = paginate.total
        user_lst = paginate.items

        uid_lst = [u.id for u in user_lst]
        uid_merchant = UserBalance.query.filter(UserBalance.id.in_(uid_lst)).all()
        mer_bl_uid = {uid.id: dict(balance=uid.real_balance, merchant=uid.merchant) for uid in uid_merchant}

        data = [dict(user_id=u.id,
                     phone_number=PhoneNumberParser.hide_number(u.account),
                     type='测试用户' if u.is_test_user else "普通用户",
                     source=mer_bl_uid[u.id]['merchant'].name,
                     available_bl=mer_bl_uid[u.id]['balance'],
                     register_datetime=u.str_create_time,
                     state=u.state.name)
                for u in user_lst]

        return UserListResult(bs_data=dict(entries=data, total=total)).as_response()


@ns.route('/user/balance/edit')
@ResponseDoc.response(ns, api)
class UserBalanceEdit(Resource):
    method_decorators = admin_decorators

    @ns.expect(UserBalanceEditApi)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        用户余额调整
        :return:
        """

        form, error = UserBalanceEditForm.request_validate()
        if error:
            return error.as_response()

        uid = form.uid.data
        # 判断该用户id是否存在
        user = User.query.filter_by(**dict(id=uid)).first()
        if not user:
            return AdjustUserBalanceError(message="系统找不到该用户").as_response()

        ad_type = BalanceAdjustTypeEnum.PLUS

        # 当调整状态为 减少时 需要判断 当前用户余额和商户余额值
        amount = BalanceKit.round_4down_5up(Decimal(form.amount.data))
        if form.adjust_type.data == BalanceAdjustTypeEnum.MINUS:
            ad_type = BalanceAdjustTypeEnum.MINUS
            # 获取用户余额 并判断
            user_balance_info = UserBalance.query.filter(UserBalance.id == uid).first()
            if not user_balance_info:
                return UserBalanceNoFoundError().as_response()

            user_balance = user_balance_info.real_balance
            if Decimal(user_balance) - amount < 0:
                print("用户没有足够的金额", user_balance, amount)
                return AdjustUserBalanceError(message="用户没有足够的金额").as_response()

            # 获取商户余额 并判断
            merchant_balance_info = MerchantInfo.query.filter_by(
                **dict(_merchant=user_balance_info.merchant.value)).first()
            if not merchant_balance_info:
                return AdjustUserBalanceError(message="该商户信息不存在").as_response()

            bl_ava = merchant_balance_info.balance_available
            if Decimal(bl_ava) - amount < 0:
                print("商户没有足够的余额", bl_ava, amount)
                return AdjustUserBalanceError(message="商户没有足够的余额").as_response()

        # 调整用户及商户余额
        flag, error = AdjustTransactionCtl.adjust_create(user=user,
                                                         source=OrderSourceEnum.MANUALLY,
                                                         amount=amount,
                                                         order_type=PayTypeEnum.MANUALLY,
                                                         bl_type=BalanceTypeEnum.AVAILABLE,
                                                         ad_type=ad_type,
                                                         comment=form.comment.data)

        if not flag:
            return AdjustUserBalanceError(message="余额调整失败").as_response()

        return ResponseSuccess().as_response()


@ns.route('/user/detail')
@ResponseDoc.response(ns, api)
class UserDetailInfo(Resource):
    method_decorators = admin_decorators

    @ns.expect(UserInfo)
    @ns.marshal_with(UserEntriesDetailResult.gen_doc(api))
    def post(self):
        """
        用户详情
        :return:
        """
        form, error = UserInfoForm.request_validate()
        if error:
            return error.as_response()

        uid = form.uid.data
        kwargs = dict(id=uid)
        entry = User.query.filter_by(**kwargs).first()
        if not entry:
            return AdjustUserBalanceError(message="系统找不到该用户").as_response()

        balance_info = UserBalance.query.filter_by(**dict(id=uid)).first()
        if not balance_info:
            return UserBalanceNoFoundError(message="用户余额数据缺失").as_response()

        head_info = dict(
            uid=uid,
            account=PhoneNumberParser.hide_number(entry.account),
            type='测试用户' if entry.is_test_user else "普通用户",
            source=entry.merchant.name,
            ava_bl=balance_info.real_balance,
            create_time=entry.str_create_time,
            state=entry.state.name
        )

        card_lst = BankCard.query.filter_by(**dict(uid=uid, valid=1)).order_by(BankCard._create_time.desc()).all()

        if not card_lst:
            bankcard_entries = []
        else:
            bankcard_entries = [dict(
                bank_id=card.card_id,
                bank_name=card.bank_name,
                account_name=card.account_name,
                card_no=card.card_no_short_description,
                province="{}/{}".format(card.province, card.city),
                branch=card.branch
            ) for card in card_lst]

        return UserEntriesDetailResult(bs_data=dict(headInfo=head_info, bankcardEntries=bankcard_entries)).as_response()


@ns.route('/user/transaction')
@ResponseDoc.response(ns, api)
class UserTransaction(Resource):
    method_decorators = admin_decorators

    @ns.expect(UserTransaction)
    @ns.marshal_with(UserDepositResult.gen_doc(api))
    def post(self):
        """
        用户最近一周充值提现交易记录
        :return:
        """

        form, error = UserTransactionForm().request_validate()
        if error:
            return error.as_response()

        uid = form.uid.data
        pay_type = form.pay_type.data
        page_size = form.page_size.data
        page_index = form.page_index.data

        entry = User.query.filter_by(**dict(id=uid)).first()
        if not entry:
            return AdjustUserBalanceError(message="系统找不到该用户").as_response()

        # 获取用户最近一周的充值提现记录
        query_datetime_lst = []
        c_date = DateTimeKit.get_cur_datetime()
        s_date = c_date + DateTimeKit.time_delta(days=-7)
        if not DateTimeKit.is_same_month(s_date, DateTimeKit.get_cur_datetime()):
            _, e_m_date = DateTimeKit.get_month_begin_end(year=s_date.year, month=s_date.month)
            s_m_date, _ = DateTimeKit.get_month_begin_end(year=c_date.year, month=c_date.month)
            s_date, _ = DateTimeKit.get_day_begin_end(s_date)
            query_datetime_lst.append([s_date, e_m_date])
            query_datetime_lst.append([s_m_date, c_date])
        else:
            s_date, _ = DateTimeKit.get_day_begin_end(s_date)
            query_datetime_lst.append([s_date, c_date])

        order_list = []
        for s_e_date in query_datetime_lst:

            if pay_type == PayTypeEnum.DEPOSIT:
                base_order = OrderDeposit.query_by_create_time(begin_time=s_e_date[0],
                                                               end_time=s_e_date[1],
                                                               merchant=entry.merchant).filter_by(
                    **dict(uid=entry.uid)).all()

                # order_detail = OrderDetailDeposit.query_by_create_time(begin_time=s_e_date[0],
                #                                                        end_time=s_e_date[1],
                #                                                        merchant=entry.merchant).filter_by(
                #     uid=entry.uid).all()
                # detail_dict = [{detail.order_id: detail} for detail in order_detail]
                [order_list.append(dict(
                    mch_tx_id=item.mch_tx_id,
                    sys_tx_id=item.sys_tx_id,
                    pay_method=item.pay_method.desc,
                    amount=item.amount,
                    tx_amount=item.tx_amount,
                    create_time=item.str_create_time,
                    state=item.state.get_back_desc(PayTypeEnum.DEPOSIT)
                )) for item in base_order]
            elif pay_type == PayTypeEnum.WITHDRAW:

                base_order = OrderWithdraw.query_by_create_time(begin_time=s_e_date[0],
                                                                end_time=s_e_date[1],
                                                                merchant=entry.merchant).filter_by(
                    **dict(uid=entry.uid)).all()
                detail_order = OrderDetailWithdraw.query_by_create_time(begin_time=s_e_date[0],
                                                                        end_time=s_e_date[1],
                                                                        merchant=entry.merchant).filter_by(
                    **dict(uid=entry.uid)).all()
                detail_dict = {detail.order_id: detail for detail in detail_order}

                bank_lst = [order.bank_id for order in base_order]

                bank_info = BankCard.query.filter(BankCard.id.in_(bank_lst)).all()

                bank_dct = {bank.id: bank for bank in bank_info}

                [order_list.append(dict(
                    mch_tx_id=item.mch_tx_id,
                    sys_tx_id=item.sys_tx_id,
                    amount=item.amount,
                    fee=detail_dict[item.order_id].fee,
                    bank_name=bank_dct[item.bank_id].bank_name,
                    card_no=bank_dct[item.bank_id].card_no_short_description,
                    state=item.state.get_back_desc(PayTypeEnum.WITHDRAW),
                    done_time=item.update_time,
                    create_time=item.str_create_time
                )) for item in base_order]

        items, total = Pagination.paginate_list(items=order_list, page_index=page_index, page_size=page_size,
                                                sort_key="create_time")

        if pay_type == PayTypeEnum.WITHDRAW:
            return UserDepositResult(
                bs_data=dict(depositInfo=dict(entries=[], total=0),
                             withdrawInfo=dict(entries=items, total=total))).as_response()
        elif pay_type == PayTypeEnum.DEPOSIT:
            return UserDepositResult(
                bs_data=dict(depositInfo=dict(entries=items, total=total),
                             withdrawInfo=dict(entries=[], total=0))).as_response()


@ns.route('/user/bank/delete')
@ResponseDoc.response(ns, api)
class UserBankDelete(Resource):
    method_decorators = admin_decorators

    @ns.expect(UserBankInfo)
    @ns.marshal_with(ResponseSuccess.gen_doc(api))
    def post(self):
        """
        用户银行信息编辑
        """
        form, error = UserBankDeleteForm().request_validate()
        if error:
            return error.as_response()

        print(form.card_id, "****************", form.card_id.data)
        card_id = form.card_id.data

        # 判断该用户银行卡 信息是否存在
        card_entry = BankCard.query.filter_by(**dict(id=card_id, valid=1)).first()
        if not card_entry:
            return AdjustUserBalanceError(message="card_id 不存在").as_response()

        BankCard.delete_bankcard_by_card_id(card_id=card_id)

        return ResponseSuccess().as_response()
