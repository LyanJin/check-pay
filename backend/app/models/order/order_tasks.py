from decimal import Decimal

from flask import current_app

from app.enums.trade import OrderStateEnum
from app.extensions import db
from app.libs.balance_kit import BalanceKit
from app.libs.datetime_kit import DateTimeKit
from app.libs.model.base import ModelBase


class OrderTasks(ModelBase):
    order_id = db.Column(db.Integer, comment='订单ID', nullable=False, unique=True)

    @classmethod
    def insert_task(cls, order_id):
        """
        插入一个任务
        :param order_id:
        :return:
        """
        model = cls()
        model.order_id = order_id
        cls.commit_models(model)
        return model

    @classmethod
    def delete_task(cls, task_id):
        """
        删除一个任务
        :param task_id:
        :return:
        """
        cls.delete_model(query_fields=dict(id=task_id), commit=True)


class OrderTransferLog(ModelBase):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False, comment='订单ID')
    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间", index=True)
    in_account = db.Column(db.Text, comment='收款银行卡号', nullable=True)
    out_name = db.Column(db.String(32), comment='出款人姓名', nullable=True)
    _amount = db.Column('amount', db.BigInteger, comment='订单发起金额', nullable=False)
    _state = db.Column('state', db.SmallInteger, comment="订单状态", nullable=False)

    @property
    def order_id(self):
        return self.id

    @order_id.setter
    def order_id(self, value):
        self.id = value

    @property
    def amount(self):
        return BalanceKit.divide_hundred(self._amount)

    @amount.setter
    def amount(self, value):
        self._amount = BalanceKit.multiple_hundred(value)

    @property
    def state(self) -> OrderStateEnum:
        return OrderStateEnum(self._state)

    @state.setter
    def state(self, value: OrderStateEnum):
        self._state = value.value

    @classmethod
    def insert_transfer_log(cls, order_id, amount, in_account=None, out_name=None):
        """
        插入一个转账日志
        :param order_id: 订单ID
        :param amount: 转账金额
        :param in_account: 收款账号
        :param out_name: 出款人姓名
        :return:
        """
        model = cls()
        model.order_id = order_id
        model.amount = amount
        model.in_account = in_account
        model.out_name = out_name
        model.state = OrderStateEnum.INIT
        try:
            cls.commit_models(model)
        except:
            current_app.logger.error('An error occurred.', exc_info=True)
            return None
        return model

    @classmethod
    def query_transfer_log(cls, order_id):
        """
        查询转账日志
        :param order_id:
        :return:
        """
        return cls.query_one(query_fields=dict(id=order_id))

    @classmethod
    def query_transfer_log_by_user_info(cls, deposit_cardnumber, amount, client_accountname=None, deposit_time=None):

        query_params = dict(in_account=deposit_cardnumber, amount=amount, state=OrderStateEnum.INIT)
        if client_accountname:
            query_params['out_name'] = client_accountname
        if deposit_time:
            begin_time = DateTimeKit.datetime_to_timestamp(
                DateTimeKit.str_to_datetime(deposit_time) + DateTimeKit.time_delta(minutes=-180))
            end_time = DateTimeKit.datetime_to_timestamp(
                DateTimeKit.str_to_datetime(deposit_time) + DateTimeKit.time_delta(minutes=80))
            if client_accountname:
                return cls.query.filter(cls._create_time >= begin_time, cls._create_time <= end_time).filter(
                    cls.in_account == deposit_cardnumber).filter(cls._amount == int(Decimal(amount)*Decimal(100))).filter(
                    cls._state == OrderStateEnum.INIT.value).filter(cls.out_name == client_accountname).all()
            else:
                return cls.query.filter(cls._create_time >= begin_time, cls._create_time <= end_time).filter(
                    cls.in_account == deposit_cardnumber).filter(cls._amount == int(Decimal(amount)*Decimal(100))).filter(
                    cls._state == OrderStateEnum.INIT.value).all()

        return cls.query_model(query_fields=query_params).all()



    @classmethod
    def delete_transfer_log_by_date(cls, someday):
        """
        删除某天的日志
        :param someday:
        :return:
        """
        return cls.delete_by_someday(someday)

    @classmethod
    def update_transfer_log(cls, order_id):

        model = cls.query_transfer_log(order_id=order_id)
        if model:
            model.state = OrderStateEnum.SUCCESS
            cls.commit_models(model)
            return True
        return False
