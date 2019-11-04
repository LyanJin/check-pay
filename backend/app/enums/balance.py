from app.enums.base_enum import BaseEnum
from app.enums.trade import BalanceTypeEnum, BalanceAdjustTypeEnum


class ManualAdjustmentType(BaseEnum):
    """调整类型"""

    PLUS = 'PLUS'
    MINUS = 'MINUS'
    FROZEN = 'FROZEN'
    UNFROZEN = 'UNFROZEN'
    MINUS_INCOME = 'MINUS_INCOME'

    @classmethod
    def description(cls, doc=True):
        kv_pairs = '; '.join([': '.join([x.name, str(x.desc)]) for x in cls])
        if not doc:
            return kv_pairs
        return "<" + cls.__doc__ + ">: " + kv_pairs

    @property
    def desc(self):
        """
        中文描述
        :return:
        """
        return {
            self.PLUS: "调整增加",
            self.MINUS: "调整扣除",
            self.FROZEN: "资金冻结",
            self.UNFROZEN: "资金解冻",
            self.MINUS_INCOME: "在途资金扣除",
        }.get(self)

    def get_balance_adjustment_type(self):
        if self.PLUS == self:
            bl_type = BalanceTypeEnum.AVAILABLE
            ad_type = BalanceAdjustTypeEnum.PLUS
        elif self.MINUS == self:
            bl_type = BalanceTypeEnum.AVAILABLE
            ad_type = BalanceAdjustTypeEnum.MINUS
        elif self.FROZEN == self:
            bl_type = BalanceTypeEnum.FROZEN
            ad_type = BalanceAdjustTypeEnum.PLUS
        elif self.UNFROZEN == self:
            bl_type = BalanceTypeEnum.FROZEN
            ad_type = BalanceAdjustTypeEnum.MINUS
        elif self.MINUS_INCOME == self:
            bl_type = BalanceTypeEnum.INCOME
            ad_type = BalanceAdjustTypeEnum.MINUS
        else:
            raise ValueError('undefined enum')
        return bl_type, ad_type
