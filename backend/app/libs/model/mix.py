import copy
import datetime
import json
import time
from decimal import Decimal
from enum import Enum

from flask import current_app

from app.constants.model import SHARD_COLUMN_FORMAT, TABLE_MAX_MONTHS, TABLE_HOT_DAYS, TABLE_BEGIN_TIME
from app.extensions import db
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.libs.string_kit import StringParser, StringUtils
from config import MerchantEnum

DEBUG_LOG = False


class ModelNotExistException(Exception):
    pass


class ShardParamsException(Exception):
    pass


class ShardDateException(ShardParamsException):
    pass


class MultiMonthQueryException(ShardParamsException):
    pass


class ModelOpMix:
    """
    模型基本操作混合类
    """
    _before_fields = None
    _after_fields = None

    def set_before_fields(self, keys: list):
        """
        设置需要[更新]的属性，不是model的所有属性
        :param keys:
        :return:
        """
        self._before_fields = dict(
            model=self.__class__.__name__,
            model_id=self.id
        )
        for key in keys:
            try:
                self._before_fields[key] = getattr(self, key)
            except Exception as e:
                print('_before_fields: %s' % self._before_fields)
                print('keys: %s' % keys)
                print('invalid key: %s' % key)
                raise e

    def get_before_fields(self):
        """
        获取已经[更新]的属性，不是model的所有属性
        :return:
        """
        return self._before_fields or dict(
            model=self.__class__.__name__,
            model_id=self.id
        )

    def set_after_fields(self, update_params: dict):
        """
        设置需要[更新]的属性，不是model的所有属性
        :param update_params:
        :return:
        """
        self._after_fields = dict(
            model=self.__class__.__name__,
            model_id=self.id
        )

        for key in update_params.keys():

            try:
                self._after_fields[key] = getattr(self, key)
            except Exception as e:
                print('_after_fields: %s' % self._after_fields)
                print('update_params: %s' % update_params)
                print('invalid key: %s' % key)
                raise e

    def get_after_fields(self):
        """
        获取已经[更新]的属性，不是model的所有属性
        :return:
        """
        return self._after_fields or dict(
            model=self.__class__.__name__,
            model_id=self.id
        )

    @classmethod
    def covert_data_to_dict(cls, value):
        data = dict()
        for k, v in value.items():
            if isinstance(v, Enum):
                v = v.to_dict()
            elif isinstance(v, Decimal):
                v = str(v)
            elif isinstance(v, (datetime.datetime, datetime.date)):
                v = DateTimeKit.datetime_to_timestamp(v)
            elif isinstance(v, dict):
                v = cls.covert_data_to_dict(v)
            elif isinstance(v, list):
                v_list = list()
                for x in v:
                    if isinstance(x, Enum):
                        x = x.to_dict()
                    elif isinstance(x, Decimal):
                        x = str(x)
                    elif isinstance(x, (datetime.datetime, datetime.date)):
                        x = DateTimeKit.datetime_to_timestamp(v)
                    elif isinstance(x, dict):
                        x = cls.covert_data_to_dict(x)
                    v_list.append(x)
                v = v_list
            data[k] = v
        return data

    @classmethod
    def commit_models(cls, *args, models=None, delete=False, commit=True):
        """
        多个model在同一个事务中提交,一个失败，所有都失败
        :param models:
        :param delete:
        :param commit: 是否提交事务
        :return:
        """
        models = models or list()
        models.extend(args)

        with db.auto_commit(commit):
            for model in models:
                if delete:
                    db.session.delete(model)
                else:
                    db.session.add(model)

    def set_attr(self, fields: dict):
        for k, v in fields.items():
            try:
                setattr(self, k, v)
            except AttributeError as e:
                print(self)
                print('k: %s, v: %s' % (k, v))
                raise e

    @classmethod
    def get_model_cls(cls, *args, **kwargs):
        return cls

    @classmethod
    def get_model_obj(cls, *args, **kwargs):
        return cls.get_model_cls(*args, **kwargs)()

    @classmethod
    def add_model(cls, fields: dict, *args, **kwargs):
        """
        新增模型
        :param fields:
        :param args:
        :param kwargs:
        :return:
        """
        model = cls.get_model_obj(*args, **kwargs)

        # 为了少改代码，临时适配 merchant 参数，后续再到每个 fields 里面新增进去
        if 'merchant' in kwargs:
            fields['merchant'] = kwargs['merchant']

        model.set_attr(fields)
        model.set_after_fields(fields)
        if kwargs.get('commit'):
            models = kwargs.get('models') or list()
            models.append(model)
            cls.commit_models(models=models)

        return dict(
            code=0,
            msg='ok',
            model=model,
        )

    @classmethod
    def update_model(cls, fields: dict, query_fields: dict, *args, **kwargs):
        """
        修改模型
        :param fields:
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        model = cls.query_one(query_fields, *args, **kwargs)
        if not model:
            return dict(
                code=-99,
                msg='未找到需要更新的模型, cls: %s, query_fields: %s' % (cls.__name__, query_fields),
                model=None,
            )

        # 为了少改代码，临时适配 merchant 参数，后续再到每个 fields 里面新增进去
        if 'merchant' in kwargs:
            fields['merchant'] = kwargs['merchant']

        model.set_before_fields(fields.keys())
        model.set_attr(fields)
        model.set_after_fields(fields)

        if kwargs.get('commit'):
            models = kwargs.get('models') or list()
            models.append(model)
            cls.commit_models(models=models)

        return dict(
            code=0,
            msg='ok',
            model=model,
        )

    @classmethod
    def delete_model(cls, query_fields: dict, *args, **kwargs):
        """
        删除模型
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        model = cls.query_model(query_fields, *args, **kwargs).first()
        if not model:
            return dict(
                code=0,
                msg='未找到需要删除的模型, cls: %s, query_fields: %s' % (cls.__name__, query_fields),
                model=None,
            )

        if kwargs.get('commit'):
            models = kwargs.get('models') or list()
            models.append(model)
            cls.commit_models(models=models, delete=True)

        return dict(
            code=0,
            msg='ok',
            model=model,
        )

    @classmethod
    def delete_all(cls, *args, **kwargs):
        """
        删除所有
        :return:
        """
        model_cls = kwargs.get('model_cls') or cls.get_model_cls(*args, **kwargs)

        with db.auto_commit():
            model_cls.query.delete()

    @classmethod
    def query_model(cls, query_fields: dict, *args, **kwargs):
        """
        查询模型
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        model_cls = kwargs.get('model_cls') or cls.get_model_cls(*args, **kwargs)
        return model_cls.query.filter_by(**query_fields)

    @classmethod
    def query_one(cls, query_fields: dict, *args, **kwargs):
        """
        查询模型
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        return cls.query_model(query_fields, *args, **kwargs).first()

    @classmethod
    def query_one_order_by(cls, query_fields: dict, order_fields: list, *args, **kwargs):
        """
        查询模型
        :param query_fields:
        :param order_fields: 根据条件排序之后再取第一个
        :param args:
        :param kwargs:
        :return:
        """
        return cls.query_model(query_fields, *args, **kwargs).order_by(*order_fields).first()

    @classmethod
    def query_all(cls, *args, **kwargs):
        """
        查询所有
        :return:
        """
        model_cls = kwargs.get('model_cls') or cls.get_model_cls(*args, **kwargs)
        return model_cls.query.all()

    @classmethod
    def query_by_id(cls, id_value, *args, **kwargs):
        """
        根据主键查询
        :param id_value:
        :param kwargs:
        :return:
        """
        return cls.query_one(query_fields=dict(id=id_value))

    @classmethod
    def query_by_create_time(cls, begin_time, end_time, *args, **kwargs):
        """
        根据时间查询数据，包含begin_time, end_time，[begin_time, end_time]
        :param begin_time:
        :param end_time:
        :return: 返回查询对象
        """
        begin_ts = DateTimeKit.datetime_to_timestamp(begin_time)
        end_ts = DateTimeKit.datetime_to_timestamp(end_time)

        model_cls = kwargs.get('model_cls') or cls.get_model_cls(*args, **kwargs)
        return model_cls.query.filter(model_cls._create_time >= begin_ts, model_cls._create_time <= end_ts)

    @classmethod
    def query_by_date(cls, someday, **kwargs):
        """
        在某天的范围内查询
        :param someday:
        :param kwargs:
        :return: 返回查询对象
        """
        begin_time, end_time = DateTimeKit.get_day_begin_end(someday)
        return cls.query_by_create_time(begin_time, end_time, **kwargs)

    @classmethod
    def delete_by_create_time(cls, begin_time, end_time, *args, **kwargs):
        """
        根据创建时间删除记录
        :param begin_time:
        :param end_time:
        :param args:
        :param kwargs:
        :return:
        """
        with db.auto_commit():
            return cls.query_by_create_time(begin_time, end_time, *args, **kwargs).delete(
                synchronize_session="fetch")

    @classmethod
    def delete_by_someday(cls, someday, **kwargs):
        """
        根据创建时间删除记录
        :param someday:
        :param kwargs:
        :return:
        """
        begin_time, end_time = DateTimeKit.get_day_begin_end(someday)
        return cls.delete_by_create_time(begin_time, end_time, **kwargs)


class ColdHotMix:
    """
    冷/热表同步，热表定期清理
    """
    _cls_mapper = dict()

    # 冷表前缀
    __cold_prefix = 'COLD'

    # 热表数据保留 HOT_DAYS 天，超过 HOT_DAYS 的数据定期删除
    HOT_DAYS = TABLE_HOT_DAYS

    @classmethod
    def is_hot_active(cls):
        """
        是否启用冷表备份
        :return:
        """
        return cls.HOT_DAYS > 0

    @classmethod
    def is_cold_table(cls):
        """
        判断是否是冷表
        :return:
        """
        name = cls.__name__.lower()
        return name.startswith(cls.__cold_prefix.lower())

    @classmethod
    def gen_cold_table_name(cls, table_name):
        """
        表名
        :return:
        """
        return StringParser('_').join([cls.__cold_prefix.lower(), table_name])

    @classmethod
    def gen_cold_class_name(cls, cls_name):
        """
        类名
        :return:
        """
        return StringParser('_').join([cls.__cold_prefix, cls_name])

    @classmethod
    def get_cold_model_cls(cls, *args, **kwargs):
        """
        查询已经存在的模型
        :return:
        """
        cls_name = cls.gen_class_name(*args, **kwargs)
        cls_name = cls.gen_cold_class_name(cls_name)
        model_cls = cls.get_exist_cls(cls_name)
        if not model_cls:
            raise ModelNotExistException('model %s not exist, kwargs: %s' % (cls_name, kwargs))
        return model_cls

    @classmethod
    def get_cold_model_obj(cls, *args, **kwargs):
        """
        获取模型类生成的对象
        :return:
        """
        return cls.get_cold_model_cls(*args, **kwargs)()

    @classmethod
    def generate_cold_cls(cls, abs_cls, suffix, bind_key):
        """
        生成模型类
        :param abs_cls:
        :param suffix:
        :param bind_key:
        :return:
        """
        # 先看原类名称
        cls_name = abs_cls.gen_class_name(bind_key, abs_cls.TABLE_PREFIX, suffix)
        table_name = abs_cls.gen_table_name(bind_key, abs_cls.TABLE_PREFIX, suffix)

        # 依据原类名称生成冷表类名称
        cls_name = abs_cls.gen_cold_class_name(cls_name=cls_name)
        table_name = abs_cls.gen_cold_table_name(table_name=table_name)

        model_cls = abs_cls._cls_mapper.get(cls_name, None)

        if model_cls is None:
            model_cls = cls.new_cls(abs_cls, table_name, cls_name, bind_key)
            abs_cls._cls_mapper[cls_name] = model_cls

            DEBUG_LOG and print('model init, %s' % model_cls.inspect())

        return model_cls

    @classmethod
    def init_models(cls, abs_cls):
        """
        为asb_model在各个商户下生成model类
        :param abs_cls:
        :return:
        """
        if abs_cls.BIND_KEYS and abs_cls.TABLE_SUFFIXES:
            for bind_key in abs_cls.BIND_KEYS:
                for suffix in abs_cls.TABLE_SUFFIXES:
                    cls.generate_cls(abs_cls, suffix, bind_key)
                    cls.generate_cold_cls(abs_cls, suffix, bind_key)

        elif abs_cls.TABLE_SUFFIXES and not abs_cls.BIND_KEYS:
            for suffix in abs_cls.TABLE_SUFFIXES:
                cls.generate_cls(abs_cls, suffix, None)
                cls.generate_cold_cls(abs_cls, suffix, None)

        elif abs_cls.BIND_KEYS and not abs_cls.TABLE_SUFFIXES:
            for bind_key in abs_cls.BIND_KEYS:
                cls.generate_cls(abs_cls, None, bind_key)
                cls.generate_cold_cls(abs_cls, None, bind_key)

        return abs_cls


class BaseMix:
    @classmethod
    def _check_required_params(cls, **kwargs):
        """
        必填参数检查
        :param kwargs:
        :return:
        """
        pass

    @classmethod
    def _parse_suffix(cls, *args, **kwargs):
        """
        表后缀
        :param args:
        :param kwargs:
        :return:
        """
        return None

    @classmethod
    def _parse_bind_key(cls, *args, **kwargs):
        """
        绑定库
        :param args:
        :param kwargs:
        :return:
        """
        return None

    @classmethod
    def get_model_cls(cls, *args, **kwargs):
        cls._check_required_params(**kwargs)
        bind_key = cls._parse_bind_key(*args, **kwargs)
        suffix = cls._parse_suffix(*args, **kwargs)
        cls_name = cls.gen_class_name(bind_key=bind_key, suffix=suffix)
        model_cls = cls.get_exist_cls(cls_name)
        if not model_cls:
            raise ModelNotExistException('model %s not exist, kwargs: %s' % (cls_name, kwargs))
        return model_cls


class MerchantMix(BaseMix):
    """
    按商户分库的模型
    """

    BIND_KEYS = [x.name for x in MerchantEnum]

    @classmethod
    def _check_required_params(cls, **kwargs):
        """
        必填参数检查
        :param kwargs:
        :return:
        """
        if 'merchant' not in kwargs or not isinstance(kwargs['merchant'], MerchantEnum):
            raise ShardParamsException('merchant is required for cls: %s, kwargs: %s' % (cls.__name__, kwargs))

    @classmethod
    def _parse_bind_key(cls, *args, **kwargs):
        """
        绑定库
        :param args:
        :param kwargs:
        :return:
        """
        return kwargs['merchant'].name

    @classmethod
    def get_merchant(cls):
        """
        获取商户名称
        :return:
        """
        return MerchantEnum.from_name(cls.get_bind_name())

    @property
    def merchant(self):
        """
        商户名称
        :return:
        """
        return self.get_merchant()


class MonthMix(BaseMix):
    """
    按月分表的模型
    """
    MAX_MONTHS = TABLE_MAX_MONTHS
    __OLDEST_DATE = TABLE_BEGIN_TIME
    TABLE_SUFFIXES = [
        DateTimeKit.datetime_to_str(x, DateTimeFormatEnum.TIGHT_MONTH_FORMAT)
        for x in DateTimeKit.gen_month_range(__OLDEST_DATE, months=MAX_MONTHS)
    ]

    @classmethod
    def is_valid_shard_date(cls, date):
        """
        判断日期是否小于最小的分表日期
        :param date:
        :return:
        """
        if date.year < cls.__OLDEST_DATE.year or (
                date.year == cls.__OLDEST_DATE.year and date.month < cls.__OLDEST_DATE.month
        ):
            return False

        return True

    @classmethod
    def _check_required_params(cls, **kwargs):
        """
        必填参数检查
        :param kwargs:
        :return:
        """
        date = kwargs.get('date')

        if not date or not DateTimeKit.is_datetime(date):
            raise ShardParamsException('date is required for cls: %s, kwargs: %s' % (cls.__name__, kwargs))

        if not cls.is_valid_shard_date(date):
            raise ShardDateException(
                'sharding date must gte %s, cls: %s, kwargs: %s' % (cls.__OLDEST_DATE, cls.__name__, kwargs))

    @classmethod
    def _parse_suffix(cls, *args, **kwargs):
        """
        表后缀
        :param args:
        :param kwargs:
        :return:
        """
        return DateTimeKit.datetime_to_str(kwargs['date'], DateTimeFormatEnum.TIGHT_MONTH_FORMAT)


class ColumnMix(BaseMix):
    """
    按模型中某个字段的值取模分表
    """
    SHARDING_COLUMN = 'id'
    SHARDING_NUM = 10
    TABLE_SUFFIXES = [SHARD_COLUMN_FORMAT % idx for idx in range(SHARDING_NUM)]

    @classmethod
    def _check_required_params(cls, **kwargs):
        if 'column' not in kwargs or not isinstance(kwargs['column'], (str, int)):
            raise ShardParamsException('column is required for cls: %s, kwargs: %s' % (cls.__name__, kwargs))

    @classmethod
    def _parse_suffix(cls, *args, **kwargs):
        """
        表后缀
        :param args:
        :param kwargs:
        :return:
        """
        idx = kwargs['column']
        if isinstance(idx, str):
            idx = StringUtils.string_to_int16(idx)
        return SHARD_COLUMN_FORMAT % (int(idx) % cls.SHARDING_NUM)


class MerchantColumnMix(MerchantMix, ColumnMix):
    """
    商户分库，按模型中某个字段的值取模分表
    """

    @classmethod
    def _check_required_params(cls, **kwargs):
        MerchantMix._check_required_params(**kwargs)
        ColumnMix._check_required_params(**kwargs)

    @classmethod
    def _parse_suffix(cls, *args, **kwargs):
        """
        表后缀
        :param args:
        :param kwargs:
        :return:
        """
        return ColumnMix._parse_suffix(*args, **kwargs)

    @classmethod
    def _parse_bind_key(cls, *args, **kwargs):
        """
        绑定库
        :param args:
        :param kwargs:
        :return:
        """
        return MerchantMix._parse_bind_key(*args, **kwargs)


class MerchantMonthMix(MerchantMix, MonthMix):
    """
    按商户分库,按月分表的模型
    """

    @classmethod
    def _check_required_params(cls, **kwargs):
        """
        必填参数检查
        :param kwargs:
        :return:
        """
        MerchantMix._check_required_params(**kwargs)
        MonthMix._check_required_params(**kwargs)

    @classmethod
    def _parse_suffix(cls, *args, **kwargs):
        """
        表后缀
        :param args:
        :param kwargs:
        :return:
        """
        return MonthMix._parse_suffix(*args, **kwargs)

    @classmethod
    def _parse_bind_key(cls, *args, **kwargs):
        """
        绑定库
        :param args:
        :param kwargs:
        :return:
        """
        return MerchantMix._parse_bind_key(*args, **kwargs)


# class MerchantMonthColdMix(MerchantMonthMix, ColdHotMix):
class MonthColdMix(MonthMix, ColdHotMix):
    """
    按商户分库，冷/热表同步，热表定期清理
    """
    _cls_mapper = dict()

    @classmethod
    def get_cold_model_cls(cls, *args, **kwargs):
        cls._check_required_params(**kwargs)
        bind_key = cls._parse_bind_key(*args, **kwargs)
        suffix = cls._parse_suffix(*args, **kwargs)
        # return super(MerchantMonthColdMix, cls).get_cold_model_cls(bind_key=bind_key, suffix=suffix)
        return super(MonthColdMix, cls).get_cold_model_cls(bind_key=bind_key, suffix=suffix)

    @classmethod
    def query_one(cls, query_fields: dict, *args, **kwargs):
        """
        查询模型
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        cls._check_required_params(**kwargs)

        kwargs['date'] = DateTimeKit.to_date(kwargs['date'])

        if not kwargs.get('only_hot') and (kwargs.get('only_cold') or kwargs['date'] <= cls.get_clean_date()):
            # 只查冷表
            model_cls = cls.get_cold_model_cls(*args, **kwargs)
            rst = super(MonthColdMix, cls).query_one(query_fields, model_cls=model_cls)
        else:
            model_cls = cls.get_model_cls(*args, **kwargs)
            rst = super(MonthColdMix, cls).query_one(query_fields, model_cls=model_cls)

        return rst

    @classmethod
    def query_by_create_time(cls, begin_time, end_time, *args, **kwargs):
        """
        根据时间查询数据，包含begin_time, end_time，[begin_time, end_time]
        只能查开始时间当月的，会有跨月查询的数据丢失
        :param begin_time:
        :param end_time:
        :return: 返回查询对象
        """
        if not DateTimeKit.is_same_month(begin_time, end_time):
            raise MultiMonthQueryException(
                'can not query between multiple months, begin_time: %s, end_time: %s' % (begin_time, end_time))

        kwargs['date'] = DateTimeKit.to_date(begin_time)

        cls._check_required_params(**kwargs)

        if not kwargs.get('only_hot') and (kwargs.get('only_cold') or kwargs['date'] <= cls.get_clean_date()):
            model_cls = cls.get_cold_model_cls(*args, **kwargs)
            rst = super(MonthColdMix, cls).query_by_create_time(begin_time, end_time, model_cls=model_cls)
        else:
            model_cls = cls.get_model_cls(*args, **kwargs)
            rst = super(MonthColdMix, cls).query_by_create_time(begin_time, end_time, model_cls=model_cls)

        merchant = kwargs.get('merchant')
        if merchant:
            rst = rst.filter_by(_merchant=merchant.value)

        return rst

    @classmethod
    def add_model(cls, fields: dict, *args, **kwargs):
        """
        新增模型
        :param fields:
        :param args:
        :param kwargs:
        :return:
        """
        models = kwargs.get('models') or list()

        # 热模型
        model_hot = cls.get_model_obj(*args, **kwargs)

        # 为了少改代码，临时适配 merchant 参数，后续再到每个 fields 里面新增进去
        if 'merchant' in kwargs:
            fields['merchant'] = kwargs['merchant']

        model_hot.set_attr(fields)
        model_hot.set_after_fields(fields)

        models.append(model_hot)

        # 冷模型
        model_cold = cls.get_cold_model_obj(*args, **kwargs)
        model_cold.set_attr(fields)
        models.append(model_cold)

        if kwargs.get('commit'):
            cls.commit_models(models=models)

        return dict(
            code=0,
            msg='ok',
            model=dict(hot=model_hot, cold=model_cold),
        )

    @classmethod
    def update_model(cls, fields: dict, query_fields: dict, *args, **kwargs):
        """
        修改模型
        :param fields:
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        models = kwargs.get('models') or list()

        # 查出热模型
        model_cls = cls.get_model_cls(*args, **kwargs)
        model_hot = super(MonthColdMix, cls).query_one(query_fields, model_cls=model_cls)
        if not model_hot:
            return dict(
                code=-99,
                msg='未找到需要更新的热模型, cls: %s, query_fields: %s, kwargs: %s' % (cls.__name__, query_fields, kwargs),
                model=None,
            )

        # 为了少改代码，临时适配 merchant 参数，后续再到每个 fields 里面新增进去
        if 'merchant' in kwargs:
            fields['merchant'] = kwargs['merchant']

        model_hot.set_before_fields(fields.keys())
        model_hot.set_attr(fields)
        model_hot.set_after_fields(fields)

        models.append(model_hot)

        # 查出冷模型
        model_cls = cls.get_cold_model_cls(*args, **kwargs)
        model_cold = super(MonthColdMix, cls).query_one(query_fields, model_cls=model_cls)
        if not model_cold:
            return dict(
                code=-98,
                msg='未找到需要更新的热模型, cls: %s, query_fields: %s, kwargs: %s' % (cls.__name__, query_fields, kwargs),
                model=None,
            )

        model_cold.set_attr(fields)
        models.append(model_cold)

        if kwargs.get('commit'):
            cls.commit_models(models=models)

        return dict(
            code=0,
            msg='ok',
            model=dict(hot=model_hot, cold=model_cold),
        )

    @classmethod
    def delete_model(cls, query_fields: dict, *args, **kwargs):
        """
        删除模型
        :param query_fields:
        :param args:
        :param kwargs:
        :return:
        """
        models = kwargs.get('models') or list()

        # 查出热模型
        model_cls = cls.get_model_cls(*args, **kwargs)
        model_hot = super(MonthColdMix, cls).query_one(query_fields, model_cls=model_cls)
        if not model_hot:
            return dict(
                code=-99,
                msg='未找到需要删除的热模型, cls: %s, query_fields: %s' % (model_cls.inspect(), query_fields),
                model=None,
            )

        models.append(model_hot)

        # 查出冷模型
        if kwargs.get('delete_cold'):
            model_cls = cls.get_cold_model_cls(*args, **kwargs)
            model_cold = super(MonthColdMix, cls).query_one(query_fields, model_cls=model_cls)
            if not model_cold:
                return dict(
                    code=-98,
                    msg='未找到需要删除的热模型, cls: %s, query_fields: %s' % (model_cls.inspect(), query_fields),
                    model=None,
                )

            models.append(model_cold)

        if kwargs.get('commit'):
            cls.commit_models(models=models, delete=True)

        return dict(
            code=0,
            msg='ok',
            model=None,
        )

    @classmethod
    def get_clean_date(cls):
        """
        获取清理日期
        :return:
        """
        return DateTimeKit.get_cur_date() - DateTimeKit.time_delta(days=cls.HOT_DAYS)

    @classmethod
    def clean_hot_table(cls, seconds=0, clean_date=None):
        """
        清理热数据
        :param seconds: 从db删除一次后等待多少秒
        :param clean_date: 清理哪一天的数据
        :return:
        """
        clean_result = list()

        if clean_date:
            clean_date = DateTimeKit.to_date(clean_date)
            if clean_date > cls.get_clean_date():
                raise RuntimeError('invalid clean date, input: %s, fix: %s', clean_date, cls.get_clean_date())
        else:
            # 清理 HOT_DAYS 天之前的那一天的数据
            clean_date = cls.get_clean_date()

        for kls in cls._cls_mapper.values():

            if not kls.is_hot_active():
                # 未开启冷/热库的跳过
                continue

            if kls.is_cold_table():
                # 跳过冷库
                continue

            def get_query_obj(_begin_ts, _end_ts):
                return kls.query.filter(kls._create_time >= _begin_ts, kls._create_time <= _end_ts)

            begin_time, end_time = DateTimeKit.get_day_begin_end(clean_date)
            begin_ts = DateTimeKit.datetime_to_timestamp(begin_time)
            end_ts = DateTimeKit.datetime_to_timestamp(end_time)

            # 先查出总共多少条数据
            counts = get_query_obj(begin_ts, end_ts).count()
            if counts == 0:
                continue

            current_app.logger.info('begin, clean_date: %s, kls: %s, counts: %s', clean_date, kls.inspect(), counts)

            with db.auto_commit():

                # 分批按小时删除
                begin_ts_1 = begin_ts
                for end_time in DateTimeKit.gen_hour_range(clean_date):
                    end_ts_1 = DateTimeKit.datetime_to_timestamp(end_time)
                    get_query_obj(begin_ts_1, end_ts_1).delete(synchronize_session="fetch")
                    begin_ts_1 = end_ts_1
                    seconds and time.sleep(seconds)

                # 删除剩余的
                get_query_obj(begin_ts, end_ts).delete(synchronize_session="fetch")

            counts = get_query_obj(begin_ts, end_ts).count()
            if counts != 0:
                current_app.logger.error('clean hot orders failed, clean_date: %s, kls: %s, counts: %s', clean_date,
                                         kls.inspect(), counts)
            else:
                current_app.logger.info('end, clean_date: %s, kls: %s, counts: %s', clean_date, kls.inspect(), counts)

            seconds and time.sleep(seconds)

            clean_result.append(dict(
                kls=kls.inspect(),
                clean_date=clean_date,
                clean_total=counts,
            ))

        return clean_result


class AdminLogMix:
    admin_log_model = None

    @classmethod
    def get_admin_log_model(cls):
        return cls.admin_log_model

    @classmethod
    def has_admin_log(cls):
        log_cls = cls.get_admin_log_model()
        if not log_cls:
            return False

        log_params = log_cls.get_extra_params()
        if not log_params:
            return False

        return True

    @classmethod
    def add_admin_log(cls, model=None, data_before=None, data_after=None):
        """
        添加日志model
        :param model:
        :param data_before:
        :param data_after:
        :return:
        """
        log_cls = cls.get_admin_log_model()
        if not log_cls:
            return

        log_params = log_cls.get_extra_params()
        if not log_params:
            return

        if data_before and data_after:
            log_params['data_before'] = data_before
            log_params['data_after'] = data_after
        elif model:
            log_params['data_before'] = model.get_before_fields()
            log_params['data_after'] = model.get_after_fields()
        else:
            raise ValueError('invalid params')

        log_model = log_cls()
        log_model.set_attr(log_params)

        return log_model
