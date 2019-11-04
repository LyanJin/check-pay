from enum import Enum


class BaseEnum(Enum):

    @classmethod
    def get_all_enums(cls):
        return [x for x in cls]

    @classmethod
    def from_name(cls, name):
        return getattr(cls, name.upper())

    @property
    def desc(self):
        """
        中文描述
        :return:
        """
        return self.name

    @classmethod
    def get_names(cls):
        return [x.name for x in cls]

    @classmethod
    def get_desc_list(cls):
        return '|'.join([x.desc for x in cls])

    @classmethod
    def get_name_list(cls):
        return '|'.join([x.name for x in cls])

    @classmethod
    def get_value_list(cls):
        return '|'.join([str(x.value) for x in cls])

    @classmethod
    def get_desc_name_pairs(cls):
        return [dict(desc=x.desc, name=x.name) for x in cls]

    @classmethod
    def get_desc_value_pairs(cls):
        return [dict(desc=x.desc, value=str(x.value)) for x in cls]

    @classmethod
    def get_name_value_pairs(cls):
        return [dict(name=x.name, value=str(x.value)) for x in cls]

    @classmethod
    def description(cls, doc=True):
        kv_pairs = ', '.join([': '.join([x.desc or x.name, str(x.value)]) for x in cls])
        if not doc:
            return kv_pairs
        return "<" + cls.__doc__.strip() + "> {" + kv_pairs + "}"

    @classmethod
    def description_name_desc(cls, doc=True, values=None):
        values = values or cls
        kv_pairs = ', '.join([': '.join([x.desc, x.name]) for x in values])
        if not doc:
            return kv_pairs
        return "<" + cls.__doc__.strip() + "> {" + kv_pairs + "}"

    @classmethod
    def description_value_desc(cls, doc=True):
        kv_pairs = ', '.join([': '.join([x.desc, str(x.value)]) for x in cls])
        if not doc:
            return kv_pairs
        return "<" + cls.__doc__.strip() + "> {" + kv_pairs + "}"

    def to_dict(self):
        return {self.name: self.value}
