from decimal import Decimal

from app.libs.balance_kit import BalanceKit
from tests import TestNoneAppBase


class BalanceKitTest(TestNoneAppBase):

    def test_balance_multiple(self):
        v = Decimal("1.12")
        v1 = BalanceKit.multiple_unit(v)
        v2 = BalanceKit.divide_unit(v1)
        self.assertEqual(v, v2)

        v = Decimal("1.1211")
        d = 10000
        v1 = BalanceKit.multiple_unit(v, d)
        v2 = BalanceKit.divide_unit(v1, d)
        self.assertEqual(v, v2)

    @classmethod
    def format_float(cls, x=0, y=0, z=0, i=0):
        return '{}.{}{}{}'.format(i, x, y, z)

    def test_balance_round(self):
        i = 1
        for x in range(0, 10):
            d = Decimal(self.format_float(x=x, i=i))
            v = BalanceKit.round_4down_5up(d)
            self.assertEqual(d, v)

            for y in range(0, 10):
                d = Decimal(self.format_float(x=x, y=y, i=i))
                v = BalanceKit.round_4down_5up(d)
                self.assertEqual(d, v)

                for z in range(0, 10):
                    # 原始值
                    d = Decimal(self.format_float(x=x, y=y, z=z, i=i))

                    # 期望值
                    if z >= 5:
                        # z进位，y自增
                        _x = x
                        _y = y + 1
                        _i = i
                        if _y >= 10:
                            # y进位，x自增
                            _y = 0
                            _x += 1
                            if _x >= 10:
                                # x进位，i自增
                                _x = 0
                                _i += 1
                        e = Decimal(self.format_float(x=_x, y=_y, i=_i))
                    else:
                        # 舍掉z
                        e = Decimal(self.format_float(x=x, y=y, i=i))

                    # 实际值
                    v = BalanceKit.round_4down_5up(d)

                    self.assertEqual(e, v, (x, y, z))
