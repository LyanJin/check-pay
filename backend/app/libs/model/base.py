from app.extensions import db
from app.libs.datetime_kit import DateTimeKit
from app.libs.model.factory import ModelFactory
from app.libs.model.mix import ModelOpMix, MonthColdMix, MonthMix, ColumnMix


class ModelFieldsBase(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增主键')
    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间")

    # 逻辑删除使用的变量
    VALID = 1
    INVALID = 0

    def __init__(self):
        self.create_time = DateTimeKit.get_cur_datetime()

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def inspect(cls):
        bind_key = getattr(cls, '__bind_key__', None)
        return 'class: {}, table: {}, db: {}'.format(cls.__name__, cls.__tablename__, bind_key)

    def __repr__(self):
        return '{}, id: {}'.format(self.inspect(), self.id)

    __str__ = __repr__

    @property
    def create_time(self):
        if self._create_time:
            return DateTimeKit.timestamp_to_datetime(self._create_time)
        else:
            return None

    @create_time.setter
    def create_time(self, value):
        self._create_time = DateTimeKit.datetime_to_timestamp(value)

    @property
    def str_create_time(self):
        if self.create_time:
            return DateTimeKit.datetime_to_str(self.create_time)
        return ''

    @classmethod
    def query_by_create_time(cls, begin_time, end_time, **kwargs):
        """
        根据时间查询数据，包含 begin_time/end_time 边界值
        :param begin_time:
        :param end_time:
        :return: 返回查询对象
        """
        begin_time = DateTimeKit.datetime_to_timestamp(begin_time)
        end_time = DateTimeKit.datetime_to_timestamp(end_time)
        return cls.query.filter(cls._create_time.between(begin_time, end_time))


class ModelBase(ModelOpMix, ModelFieldsBase):
    """
    单库，单表模型
    """
    __abstract__ = True


class ColumnBase(ColumnMix, ModelFactory, ModelBase):
    """
    单库，按列分表
    """
    __abstract__ = True


class MonthBase(MonthMix, ModelFactory, ModelBase):
    """
    单库，按月分表
    """
    __abstract__ = True


class MonthColdBase(MonthColdMix, ModelFactory, ModelBase):
    """
    单库，按月分表
    """
    __abstract__ = True


# class MerchantBase(MerchantMix, ModelFactory, ModelBase):
#     """
#     商户分库
#     """
#     __abstract__ = True
#     _cls_mapper = dict()
MerchantBase = ModelBase


# class MerchantColumnBase(MerchantColumnMix, ModelFactory, ModelBase):
#     """
#     商户分库，按模型中某个字段的值取模分表
#     """
#     __abstract__ = True
#     _cls_mapper = dict()
MerchantColumnBase = ColumnBase


# class MerchantMonthBase(MerchantMonthMix, ModelFactory, ModelBase):
#     """
#     商户分库，按月分表
#     """
#     __abstract__ = True
#     _cls_mapper = dict()
MerchantMonthBase = MonthBase

# class MerchantMonthColdBase(MerchantMonthColdMix, ModelFactory, ModelBase):
#     """
#     商户分库，冷/热同步，冷表按月分表，热表定期清理
#     """
#     __abstract__ = True
#     _cls_mapper = dict()
MerchantMonthColdBase = MonthColdBase
