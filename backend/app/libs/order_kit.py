import hashlib
import random

from app.libs.datetime_kit import DateTimeKit
from app.libs.string_kit import StringParser, RandomString
from config import MerchantEnum


class OrderUtils:
    SEPARATOR = '|'
    PREFIX_LENGTH = 16

    # @classmethod
    # def parse_tx_id_old(cls, tx_id):
    #     """
    #     解析交易ID
    #     :param tx_id:
    #     :return: (merchant, create_time, order_id, uid)
    #     """
    #     merchant, timestamp, order_id, uid = StringParser(cls.SEPARATOR).split(tx_id)
    #     timestamp = int('0x' + timestamp, 16)
    #     order_id = int('0x' + order_id, 16)
    #     uid = int('0x' + uid, 16)
    #     try:
    #         merchant = MerchantEnum(int(merchant))
    #     except:
    #         merchant = MerchantEnum.from_name(merchant)
    #     return merchant, DateTimeKit.timestamp_to_datetime(timestamp), order_id, uid

    @classmethod
    def parse_tx_id(cls, tx_id):
        # if cls.SEPARATOR in tx_id:
        #     _, _, order_id, _ = cls.parse_tx_id_old(tx_id)
        #     return order_id
        order_id = tx_id[cls.PREFIX_LENGTH:]
        # print(order_id, len(order_id))
        return int(order_id)

    # @classmethod
    # def gen_unique_tx_id(cls, create_time, order_id, uid):
    #     """
    #     生成唯一的交易ID
    #     :param create_time:
    #     :param order_id:
    #     :param uid:
    #     :return:
    #     """
    #     create_time = DateTimeKit.datetime_to_timestamp(create_time)
    #     create_time = hex(create_time)[2:]
    #     order_id = hex(order_id)[2:]
    #     uid = hex(uid)[2:]
    #     return StringParser(cls.SEPARATOR).join([create_time, order_id, uid]).upper()

    @classmethod
    def generate_mch_tx_id(cls, order_id):
        """
        生成商户交易ID
        :param order_id:
        :return:
        """
        return cls.gen_normal_tx_id(order_id, prefix='M')

    @classmethod
    def generate_sys_tx_id(cls, order_id):
        """
        生成系统交易ID
        :param order_id:
        :return:
        """
        return cls.gen_normal_tx_id(order_id, prefix='E')

    @classmethod
    def gen_unique_ref_id(cls):
        """
        生成唯一票据ID
        :return:
        """
        return hashlib.md5(RandomString.gen_random_str(length=128).encode('utf8')).hexdigest()

    @classmethod
    def gen_normal_tx_id(cls, order_id, prefix='X'):
        """
        生成唯一交易ID
        :return:
        """
        # 前缀长度固定，时间+随机数
        s = str(DateTimeKit.get_cur_timestamp(10000)) + str(random.randint(10, 99))
        len_s = len(s)
        if len_s > cls.PREFIX_LENGTH:
            s = s[:cls.PREFIX_LENGTH]

        order_id = str(order_id).zfill(8)
        # print(order_id, len(order_id))
        s += order_id
        s = prefix + s[1:]
        return s

    @classmethod
    def parse_tx_id_time(cls, tx_id):
        s = '1' + tx_id[1:10]
        print(s)
        return DateTimeKit.timestamp_to_datetime(int(s))

    @classmethod
    def is_sys_tx_id(cls, tx_id):
        """
        以E开头，并且能解析出时间，结尾是整数订单号，就是系统交易ID
        :param tx_id:
        :return:
        """
        try:
            if not tx_id.startswith('E'):
                raise
            cls.parse_tx_id_time(tx_id)
            cls.parse_tx_id(tx_id)
            return True
        except:
            return False


if __name__ == '__main__':
    t = 'E56758249531978600000039'
    print(OrderUtils.parse_tx_id_time(t))

    # tx_id = OrderUtils.gen_normal_tx_id(1)
    # print(tx_id)
    # print(len(str(tx_id)))

    # for x in range(100):
    #     for e in [10000, 999999999999]:
    #         m = MerchantEnum.TEST
    #         t = DateTimeKit.get_cur_datetime()
    #         o = random.randint(1, e)
    #         u  = random.randint(1, e)
    #         s = OrderUtils.generate_sys_tx_id(m, t, o, u)
    #         rst = OrderUtils.parse_tx_id(s)
    #         print(s, rst)
    #         assert rst[0] == m, (rst[0], m)
    #         assert rst[1] == t, (rst[1], t)
    #         assert rst[2] == o, (rst[2], o)
    #         assert rst[3] == u, (rst[3], u)

    for e in [1, 1000000, 999999999999]:
        tx = OrderUtils.generate_sys_tx_id(e)
        o_id = OrderUtils.parse_tx_id(tx)
        print(tx, len(tx), o_id)
        assert o_id == e, (o_id, e)
