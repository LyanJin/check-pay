from decimal import Decimal

from app.enums.trade import PaymentFeeTypeEnum
from app.libs.balance_kit import BalanceKit


class FeeCalculator:
    """
    订单费用计算
    """

    @classmethod
    def calc_offer(cls, amount, tx_amount):
        """
        计算优惠金额
        :param amount:
        :param tx_amount:
        :return:
        """
        return amount - tx_amount

    @classmethod
    def calc_fee(cls, amount: Decimal, fee_type: PaymentFeeTypeEnum, fee_value: Decimal):
        """
        计算手续费: 我们收取下游商户的手续费
        :param amount:
        :param fee_type:
        :param fee_value:
        :return:
        """
        if fee_type == PaymentFeeTypeEnum.PERCENT_PER_ORDER:
            return BalanceKit.round_4down_5up(Decimal(amount) * fee_value / Decimal(str(100.0)))
        return fee_value

    @classmethod
    def calc_cost(cls, amount, fee_type: PaymentFeeTypeEnum, fee_value: Decimal):
        """
        计算成本: 通道收取的手续费
        :param amount:
        :param fee_type:
        :param fee_value:
        :return:
        """
        if fee_type == PaymentFeeTypeEnum.PERCENT_PER_ORDER:
            return BalanceKit.round_4down_5up(amount * fee_value / Decimal(100.0))
        return fee_value

    @classmethod
    def calc_profit(cls, merchant_fee, channel_cost):
        """
        盈利=商户手续费-通道手续费
        :param merchant_fee:
        :param channel_cost:
        :return:
        """
        return merchant_fee - Decimal(channel_cost)
