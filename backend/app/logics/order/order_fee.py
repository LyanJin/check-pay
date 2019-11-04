from app.logics.order.fee_calculator import FeeCalculator
from app.models.channel import ABSChannelConfig
from app.models.merchant import MerchantFeeConfig


class OrderFeeHelper:
    """
    计算一笔订单的各种费用
    """

    @classmethod
    def calc_order_fee(cls, order, tx_amount, channel_config: ABSChannelConfig, merchant_config: MerchantFeeConfig):
        """
        计算一笔订单的各种费用
        :param order: 订单对象
        :param tx_amount: 实际支付金额
        :param channel_config: 通道费率配置
        :param merchant_config: 商户费率配置
        :return:
        """
        # 计算优惠金额
        offer = FeeCalculator.calc_offer(order.amount, tx_amount)
        # 我们收取下游商户的手续费
        merchant_fee = FeeCalculator.calc_fee(order.amount, merchant_config.fee_type,
                                              merchant_config.value)
        # 通道收取的手续费
        channel_cost = FeeCalculator.calc_cost(order.amount, channel_config.fee_type, channel_config.fee)
        # 计算利润
        profit = FeeCalculator.calc_profit(merchant_fee, channel_cost)

        return dict(
            offer=offer,
            profit=profit,
            merchant_fee=merchant_fee,
            channel_cost=channel_cost,
        )
