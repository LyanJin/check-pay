from app.constants.trade import MAX_BALANCE_BIT
from decimal import Decimal


class BalanceKit:
    """
    金额工具包
    """

    @classmethod
    def multiple_unit(cls, value, unit=MAX_BALANCE_BIT):
        """
        把小数的金额转换为以分钱为单位的整数
        没有位数保留，如果出现位数舍弃或者舍入，都是错误的
        逆运算出来的值要与原始值相等
        1.12元 ==> 112分
        :param value: 只接受 Decimal, str, ex: Decimal("1.12") or "1.12"
        :param unit:
        :return:
        """
        if not isinstance(value, (Decimal, int, str)):
            raise ValueError('value must be a type of Decimal or string')
        # print(value)
        d_value = Decimal(str(value))
        d_unit = Decimal(unit)
        result = int(d_value * d_unit)

        r_value = Decimal(result) / d_unit
        assert d_value == r_value

        return result

    @classmethod
    def divide_unit(cls, value: int, unit=MAX_BALANCE_BIT):
        """
        把整数的分钱转换为元单位的小数
        没有位数保留，如果出现位数舍弃或者舍入，都是错误的
        逆运算出来的值要与原始值相等
        112分 ==> 1.12元
        :param value: 只接受整形
        :param unit:
        :return:
        """
        if not isinstance(value, int):
            raise ValueError('value must be a type of integer')

        d_value = Decimal(str(value))
        d_unit = Decimal(unit)
        result = d_value / d_unit

        r_value = int(Decimal(result) * d_unit)
        assert d_value == r_value

        return result

    yuan_to_fen = multiple_hundred = multiple_unit
    fen_to_yuan = divide_hundred = divide_unit

    @classmethod
    def round_4down_5up(cls, amount: Decimal, bit=2):
        """
        四舍五入
        :param amount:
        :param bit:
        :return:
        """
        amount += Decimal('0.000000001')
        return round(amount, bit)
