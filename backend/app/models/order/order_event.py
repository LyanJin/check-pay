import json

from app.extensions import db
from app.libs.model.base import MerchantMonthBase
from config import MerchantEnum


@MerchantMonthBase.init_models
class OrderEvent(MerchantMonthBase):
    """
    订单状态变更事件
    """
    __abstract__ = True

    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="事件发生时间", index=True)
    order_id = db.Column(db.BigInteger, nullable=False, comment='订单ID', index=True)
    uid = db.Column(db.BigInteger, nullable=False, comment='用户ID', index=True)
    ref_id = db.Column(db.String(length=32), comment="票据ID", nullable=False, unique=True)

    _data_before = db.Column('data_before', db.Text, comment="修改之前的内容")
    _data_after = db.Column('data_after', db.Text, comment="修改之后的内容")

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def data_before(self) -> list:
        value_list = list()
        if not self._data_before:
            return value_list
        for value in json.loads(self._data_before):
            value_list.append(json.loads(value))
        return value_list

    @data_before.setter
    def data_before(self, values: list):
        value_list = list()
        for value in values:
            value_list.append(json.dumps(self.covert_data_to_dict(value)))
        self._data_before = json.dumps(value_list)

    @property
    def data_after(self) -> list:
        value_list = list()
        if not self._data_after:
            return value_list
        for value in json.loads(self._data_after):
            value_list.append(json.loads(value))
        return value_list

    @data_after.setter
    def data_after(self, values: list):
        value_list = list()
        for value in values:
            value_list.append(json.dumps(self.covert_data_to_dict(value)))
        self._data_after = json.dumps(value_list)
