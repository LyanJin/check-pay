import json
from decimal import Decimal

from app.enums.trade import PayTypeEnum, OrderStateEnum, PayMethodEnum, OrderSourceEnum
from app.extensions import db
from app.libs.datetime_kit import DateTimeKit
from app.libs.model.base import MerchantMonthColdBase, ModelBase
from app.libs.order_kit import OrderUtils
from app.models.order.order import OrderBase
from config import MerchantEnum


class OrderTstGid(ModelBase):

    @classmethod
    def generate_order_id(cls):
        obj = cls()
        cls.commit_models(obj)
        return obj.id


@MerchantMonthColdBase.init_models
class OrderDepositTst(OrderBase):
    """
    测试充值订单
    """
    __abstract__ = True

    result_url = db.Column(db.String(256), comment="重定向URL", nullable=True)

    @property
    def order_type(self) -> PayTypeEnum:
        return PayTypeEnum.DEPOSIT

    @property
    def repr_amount(self):
        # 充值是正数
        return self.amount

    @classmethod
    def create_order(cls):
        merchant = MerchantEnum.TEST
        order_id = OrderTstGid.generate_order_id()
        create_time = DateTimeKit.get_cur_datetime()

        fields = dict(
            uid=0,
            create_time=create_time,
            update_time=create_time,
            order_id=order_id,
            amount=Decimal("234142.33"),
            mch_tx_id=OrderUtils.generate_mch_tx_id(order_id),
            sys_tx_id=OrderUtils.generate_sys_tx_id(order_id),
            source=OrderSourceEnum.MANUALLY,
            state=OrderStateEnum.INIT,
            op_account='test',
            pay_method=PayMethodEnum.ZHIFUBAO_SAOMA,
            notify_url="https://google.com",
            result_url="https://google.com",
            extra=json.dumps(dict(x=1, y=2, z=3)),
        )

        rst = cls.add_model(fields, merchant=merchant, date=create_time, commit=True)
        return rst

    @classmethod
    def count_all_records(cls):
        merchant = MerchantEnum.TEST
        create_time = DateTimeKit.get_cur_datetime()
        begin, end = DateTimeKit.get_month_begin_end(create_time.year, create_time.month)
        return cls.query_by_create_time(begin, end, merchant=merchant, date=create_time).count()

    @classmethod
    def drop_all_records(cls):
        create_time = DateTimeKit.get_cur_datetime()

        with db.auto_commit():
            model_cls = cls.get_model_cls(date=create_time)
            model_cls.query.delete()
            model_cls = cls.get_cold_model_cls(date=create_time)
            model_cls.query.delete()
