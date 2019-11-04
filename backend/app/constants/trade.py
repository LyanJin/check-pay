"""
交易相关的常量定义
"""

# 金额的最多保留2位小数
MAX_BALANCE_BIT = 100

# 每天支付密码最大错误次数
PAYMENT_PASSWORD_ERROR_LIMIT_TIMES = 5

# 最多能添加几张银行卡
USER_BANK_CARD_NUM_LIMIT = 8

# 刚刚发起的充值订单未完成支付的有效时间，超过这个时间订单将失效，不能再支付
DEPOSIT_ORDER_TTL = 5 * 60

# 转账限额
TRANSFER_AMOUNT_LIMIT = 45000
