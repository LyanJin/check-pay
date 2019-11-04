from app.enums.trade import PayTypeEnum, OrderStateEnum, CostTypeEnum
from app.libs.string_kit import PhoneNumberParser
from app.logics.pagination.paginate_list import Pagination
from app.models.balance import UserBalanceEvent
from app.models.bankcard import BankCard
from app.models.merchant import MerchantFeeConfig
from app.models.order.order import OrderWithdraw, OrderDeposit
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw


class TransactionListHelper:
    """
    交易记录列表处理
    """

    @classmethod
    def fill_order_item(cls, order, banks_dict: dict, order_detail_dict: dict):
        """
        提现/充值订单详情
        :param order:
        :param banks_dict:
        :param order_detail_dict:
        :return:
        """
        rst = dict(
            # 提现是负数，充值是正数
            amount=order.repr_amount,
            create_time=order.create_time,
            status=order.state.get_cashier_desc(order.order_type),
            order_type=order.order_type.desc,
            tx_id=order.sys_tx_id,
            pay_method=order.pay_method.desc if order.pay_method else '',
        )

        if isinstance(order, (OrderWithdraw,)):
            bank_card = banks_dict[order.bank_id]
            rst.update(bank_info=bank_card.short_description)

            # 用户提现手续费
            detail = order_detail_dict.get(order.order_id)
            if detail and detail.cost_type == CostTypeEnum.USER:
                rst.update(fee=detail.fee)

        return rst

    @classmethod
    def query_order_list(cls, uid, merchant, begin_time, end_time, payment_type=None):
        """
        查询订单列表
        :param uid:
        :param merchant:
        :param begin_time:
        :param end_time:
        :param payment_type:
        :return:
        """
        order_items = []

        deposit_query = OrderDeposit.query_by_create_time(
            begin_time=begin_time, end_time=end_time, merchant=merchant
        ).filter_by(uid=uid)

        withdraw_query = OrderWithdraw.query_by_create_time(
            begin_time=begin_time, end_time=end_time, merchant=merchant
        ).filter_by(uid=uid)

        if payment_type == PayTypeEnum.DEPOSIT:
            order_items.extend(deposit_query)
        elif payment_type == PayTypeEnum.WITHDRAW:
            order_items.extend(withdraw_query)
        else:
            order_items.extend(deposit_query)
            order_items.extend(withdraw_query)

        return order_items

    @classmethod
    def query_order_detail_dict(cls, uid, merchant, begin_time, end_time, payment_type=None):
        """
        查询订单详情列表
        :param uid:
        :param merchant:
        :param begin_time:
        :param end_time:
        :param payment_type:
        :return:
        """
        order_items = []

        deposit_query = OrderDetailDeposit.query_by_create_time(
            begin_time=begin_time, end_time=end_time, merchant=merchant
        ).filter_by(uid=uid)

        withdraw_query = OrderDetailWithdraw.query_by_create_time(
            begin_time=begin_time, end_time=end_time, merchant=merchant
        ).filter_by(uid=uid)

        if payment_type == PayTypeEnum.DEPOSIT:
            order_items.extend(deposit_query)
        elif payment_type == PayTypeEnum.WITHDRAW:
            order_items.extend(withdraw_query)
        else:
            order_items.extend(deposit_query)
            order_items.extend(withdraw_query)

        return {o.order_id: o for o in order_items}

    @classmethod
    def query_bank_card_dict(cls, merchant, orders):
        """
        提款订单要显示银行卡信息
        :param merchant:
        :param orders:
        :return:
        """
        bank_ids = [o.bank_id for o in orders if isinstance(o, (OrderWithdraw,))]
        banks_dict = dict()
        for bank in BankCard.query_bankcards_by_bank_ids(merchant, bank_ids).all():
            banks_dict[bank.card_id] = bank
        return banks_dict

    @classmethod
    def fill_event(cls, event: UserBalanceEvent, order_dict: dict = None, banks_dict: dict = None):
        rst = dict(
            amount=event.value_real,
            create_time=event.create_time,
            status=OrderStateEnum.SUCCESS.desc,
            order_type=event.order_type.desc,
        )

        if event.order_type == PayTypeEnum.TRANSFER:
            rst.update(
                out_account=event.mask_out_account,
                in_account=event.mask_in_account,
                comment=event.comment,
                tx_id=event.tx_id,
            )

        if event.order_type == PayTypeEnum.REFUND:
            order = order_dict[event.tx_id]
            bank_card = banks_dict[order.bank_id]
            rst.update(bank_info=bank_card.short_description)
            rst.update(
                comment=event.comment,
                tx_id=event.tx_id,
            )

        return rst

    @classmethod
    def query_balance_event(cls, uid, merchant, date, order_type: PayTypeEnum):
        """
        查询转账列表
        :param uid:
        :param merchant:
        :param order_type:
        :param date:
        :return:
        """
        return UserBalanceEvent.query_event(
            uid=uid,
            order_type=order_type,
            merchant=merchant,
            date=date
        ).all()

    @classmethod
    def query_multi_order_type_event(cls, uid, merchant, date):
        """
        查询转账列表
        :param uid:
        :param merchant:
        :param date:
        :return:
        """
        order_types = [PayTypeEnum.TRANSFER, PayTypeEnum.MANUALLY, PayTypeEnum.REFUND]
        return UserBalanceEvent.query_by_order_types(
            uid=uid,
            order_types=order_types,
            merchant=merchant,
            date=date
        ).all()

    @classmethod
    def get_transaction_list(cls, payment_type, uid, merchant, begin_time, end_time, page_size, page_index):
        """
        查询交易历史记录
        :param payment_type: 
        :param uid: 
        :param merchant: 
        :param begin_time: 
        :param end_time: 
        :param page_size: 
        :param page_index: 
        :return: 
        """
        item_list = list()
        order_dict = dict()
        banks_dict = dict()

        if not payment_type or PayTypeEnum.is_order_pay(payment_type) or PayTypeEnum.REFUND == payment_type:
            # 包含充值/提款
            order_list = cls.query_order_list(uid=uid, merchant=merchant, begin_time=begin_time,
                                              end_time=end_time, payment_type=payment_type)
            order_dict = dict([(o.sys_tx_id, o) for o in order_list])
            banks_dict = cls.query_bank_card_dict(merchant, order_list)
            order_detail_dict = cls.query_order_detail_dict(uid=uid, merchant=merchant, begin_time=begin_time,
                                                            end_time=end_time, payment_type=payment_type)

            if PayTypeEnum.REFUND != payment_type:
                item_list.extend([cls.fill_order_item(item, banks_dict, order_detail_dict) for item in order_list])

        if not payment_type:
            # 所有其它类型
            _item_list = cls.query_multi_order_type_event(uid=uid, merchant=merchant, date=begin_time)
            item_list.extend([cls.fill_event(item, order_dict, banks_dict) for item in _item_list])

        else:
            if PayTypeEnum.TRANSFER == payment_type:
                # 转账
                _item_list = cls.query_balance_event(uid=uid, merchant=merchant, date=begin_time,
                                                     order_type=payment_type)
                item_list.extend([cls.fill_event(item) for item in _item_list])

            elif PayTypeEnum.REFUND == payment_type:
                # 退款
                _item_list = cls.query_balance_event(uid=uid, merchant=merchant, date=begin_time,
                                                     order_type=payment_type)
                item_list.extend([cls.fill_event(item, order_dict, banks_dict) for item in _item_list])

            elif PayTypeEnum.MANUALLY == payment_type:
                # 手动修改，系统调整
                _item_list = cls.query_balance_event(uid=uid, merchant=merchant, date=begin_time,
                                                     order_type=payment_type)
                item_list.extend([cls.fill_event(item) for item in _item_list])

        return Pagination.paginate_list(item_list, page_size, page_index, sort_key='create_time')
