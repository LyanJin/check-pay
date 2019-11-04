from app.enums.trade import BalanceTypeEnum, SettleTypeEnum
from app.libs.datetime_kit import DateTimeKit


class SettleHelper:

    @classmethod
    def get_balance_type_by_settle(cls, settle_type: SettleTypeEnum):
        """
        根据结算类型获取商户余额变更类型
        :param settle_type: 
        :return: 
        """
        if settle_type == SettleTypeEnum.D0:
            balance_type = BalanceTypeEnum.AVAILABLE
        elif settle_type == SettleTypeEnum.T0:
            if DateTimeKit.is_weekday():
                balance_type = BalanceTypeEnum.INCOME
            else:
                balance_type = BalanceTypeEnum.AVAILABLE
        else:
            balance_type = BalanceTypeEnum.INCOME

        return balance_type
