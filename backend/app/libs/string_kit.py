import hashlib
import random
from collections.abc import Iterable
from enum import Enum

import phonenumbers


class CharOp(Enum):
    # 包含大写字符
    U = 1
    # 包含小写字符
    L = 2
    # 包含数字
    N = 3
    # 包含特殊字符
    S = 4


class RandomString:
    """
    随机字符串生成器
    """
    # 所有大写字母
    uppers = tuple(chr(i) for i in range(65, 91))
    # 所有小写字母
    lowers = tuple(chr(i) for i in range(97, 123))
    # 所有数字
    numbers = tuple(chr(i) for i in range(48, 58))
    # 可视的特殊字符串
    specials = tuple(i for i in "!#%^&*(-_=+)")

    @classmethod
    def gen_random_str(cls, length=32, options=(CharOp.N,)):
        """
        随机字符串
        :param length:
        :param options:
        :return:
        """
        assert length > 0

        if not isinstance(options, Iterable):
            options = (options,)

        chars = []

        if CharOp.U in options:
            chars.extend(cls.uppers)
        if CharOp.L in options:
            chars.extend(cls.lowers)
        if CharOp.N in options:
            chars.extend(cls.numbers)
        if CharOp.S in options:
            chars.extend(cls.specials)

        if not chars:
            raise ValueError('invalid options: %s' % options)

        if len(chars) < length:
            chars *= int(length / len(chars) + 1)

        random.shuffle(chars)
        chars = chars[:length]

        return ''.join(chars)

    @classmethod
    def random_md5_string(cls):
        import hashlib
        import os
        array = os.urandom(1 << 20)
        md5 = hashlib.md5()
        md5.update(array)
        return md5.hexdigest()

    @classmethod
    def gen_md5_string(cls, sign):
        import hashlib
        md5 = hashlib.md5()
        md5.update(sign)
        return md5.hexdigest()


class StringParser:
    # 分隔符
    sp_char = '|'

    def __init__(self, sp_char=None, to_type=str):
        if sp_char:
            self.sp_char = sp_char

        self.to_type = to_type

    def join(self, str_list):
        """
        组合字符串
        :param str_list:
        :return:
        """
        return self.sp_char.join([str(self.to_type(s)) for s in str_list])

    def split(self, list_str, b=None, e=None):
        """
        分割字符串
        :param list_str:
        :param b:
        :param e:
        :return:
        """
        b = b or 0
        e = e or len(list_str)
        return list(map(self.to_type, list_str.split(self.sp_char)[b:e]))


class PhoneNumberParser:

    @classmethod
    def is_valid_number(cls, phone_number):
        """
        判断传入字符串是不是一个有效的手机号码
        :param phone_number:
        :return:
        """
        try:
            phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

        return phonenumbers.is_valid_number(phone_number)

    @classmethod
    def get_country_code(cls, phone_number):
        """
        从手机号码中解析国家代码（区号）
        :param phone_number:
        :return:
        """
        try:
            phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return None

        return phone_number.country_code

    @classmethod
    def hide_number(cls, phone_number, pre_index=3, suffix_index=-4):
        if not phone_number:
            return ''
        rst = phonenumbers.parse(phone_number)
        country_code = str(rst.country_code)
        national_number = str(rst.national_number)
        return '+' + str(country_code) + national_number[:pre_index] + '****' + national_number[suffix_index:]


class StringUtils:
    @classmethod
    def camel_to_underline(cls, s):
        """
        把驼峰命名的字符串转换为小写+下划线
        :param s:
        :return:
        """
        if not isinstance(s, str):
            return s

        return ''.join([c if c.islower() else '_' + c.lower() for c in s.strip()]).strip('_')

    @classmethod
    def string_to_int16(cls, string):
        return int(string, 16)


if __name__ == '__main__':
    #print(RandomString.random_md5_string())
    print(RandomString.gen_random_str(64, [CharOp.L, CharOp.N, CharOp.S, CharOp.U]))
