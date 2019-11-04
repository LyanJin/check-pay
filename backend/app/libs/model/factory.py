from app.extensions import db
from app.libs.string_kit import StringParser, StringUtils

DEBUG_LOG = False


class ModelFactory:
    _cls_mapper = dict()

    UNION_UNIQUE_INDEX = []
    UNION_INDEX = []

    BIND_KEYS = []
    TABLE_SUFFIXES = []
    TABLE_PREFIX = ""

    @classmethod
    def get_bind_name(cls):
        """
        获取绑定库的名称
        :return:
        """
        return getattr(cls, '__bind_key__', None)

    @classmethod
    def is_table_exists(cls, model_cls):
        """
        判断数据库中是否存在这个表
        :param model_cls:
        :return:
        """
        bind = cls.get_bind_name()
        engine = db.get_engine(bind=bind)
        return model_cls.metadata.tables[model_cls.__tablename__].exists(engine)

    @classmethod
    def get_exist_cls(cls, cls_name):
        return cls._cls_mapper.get(cls_name)

    @classmethod
    def get_cls_mapper(cls):
        return cls._cls_mapper

    @classmethod
    def __join_names(cls, bind_key, prefix, suffix, camel_cls):
        """前缀_类名_库名_后缀"""
        values = list()

        if prefix:
            values.append(prefix)

        values.append(cls.__name__ if camel_cls else StringUtils.camel_to_underline(cls.__name__))

        if bind_key:
            values.append(bind_key)

        if suffix:
            values.append(suffix)

        return StringParser('_').join(values)

    @classmethod
    def gen_table_name(cls, bind_key=None, prefix=None, suffix=None):
        return cls.__join_names(bind_key, prefix, suffix, False)

    @classmethod
    def gen_class_name(cls, bind_key=None, prefix=None, suffix=None):
        return cls.__join_names(bind_key, prefix, suffix, True)

    @classmethod
    def new_cls(cls, abs_cls, table_name, cls_name, bind_key=None):
        """
        生成模型类
        :param abs_cls:
        :param table_name:
        :param cls_name:
        :param bind_key:
        :return:
        """
        # 使用抽象类来生成子类
        indexes = list()
        for v in abs_cls.UNION_UNIQUE_INDEX:
            indexes.append(db.UniqueConstraint(*v, name='uix_' + table_name + '_' + '_'.join(v)))
        for v in abs_cls.UNION_INDEX:
            indexes.append(db.Index('ix_' + table_name + '_' + '_'.join(v), *v))

        return type(cls_name, (abs_cls,), dict(
            __module__=abs_cls.__module__,
            __name__=cls_name,
            __tablename__=table_name,
            __bind_key__=bind_key,
            __table_args__=tuple(indexes),
        ))

    @classmethod
    def generate_cls(cls, abs_cls, suffix, bind_key):
        """
        生成模型类
        :param abs_cls:
        :param suffix:
        :param bind_key:
        :return:
        """
        cls_name = abs_cls.gen_class_name(bind_key, abs_cls.TABLE_PREFIX, suffix)
        table_name = abs_cls.gen_table_name(bind_key, abs_cls.TABLE_PREFIX, suffix)

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
        BIND_KEYS = getattr(abs_cls, 'BIND_KEYS', None)

        if BIND_KEYS and abs_cls.TABLE_SUFFIXES:
            for bind_key in BIND_KEYS:
                for suffix in abs_cls.TABLE_SUFFIXES:
                    cls.generate_cls(abs_cls, suffix, bind_key)

        elif abs_cls.TABLE_SUFFIXES and not BIND_KEYS:
            for suffix in abs_cls.TABLE_SUFFIXES:
                cls.generate_cls(abs_cls, suffix, None)

        elif BIND_KEYS and not abs_cls.TABLE_SUFFIXES:
            for bind_key in BIND_KEYS:
                cls.generate_cls(abs_cls, None, bind_key)

        return abs_cls
