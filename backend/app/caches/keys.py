"""
缓存键定义，统一管理
"""

# 验证码缓存
AUTH_CODE_CACHE_KEY_PREFIX = 'auth_code'

# 当日该验证码发送次数 最大为5
AUTH_CODE_LIMITER_CACHE_KEY_PREFIX = 'code_limit'

# 商户域名缓存，域名到商户名称的映射
DOMAIN_CACHE_HASH_KEY_PREFIX = 'domain'

# 用户登录状态缓存
USER_LOGIN_CACHE_KEY_PREFIX = 'login'

# 当日该用户允许密码连续输错次数
LOGIN_PASSWORD_LIMITER_CACHE_KEY_PREFIX = 'password_limit'

# 后台用户登录状态缓存
ADMIN_LOGIN_CACHE_KEY_PREFIX = 'login_admin'

# 商户后台用户登录状态缓存
MERCHANT_LOGIN_CACHE_KEY_PREFIX = 'login_merchant_admin'

# 当日该用户允许交易密码连续输错次数
LOGIN_PAYMENT_PASSWORD_LIMITER_CACHE_KEY_PREFIX = 'payment_password_limit'

# 暂存充值订单的跳转页面内容
PAGE_RENDER_CACHE_KEY_PREFIX = 'payment'

# 通道限额
CHANNEL_LIMIT_KEY_PREFIX = "channel_limit"

# 通道当天累积限额
CHANNEL_DAY_LIMIT_KEY_PREFIX = "channel_day_limit"

# Epay Tong 提现订单 列表
EPAY_TONG_WITHDRAW_KEY_PREFIX = "epay_tong_withdraw_order"

# 用户标签缓存
USER_FLAG_CACHE_KEY_PREFIX = 'user_flag_hash'
