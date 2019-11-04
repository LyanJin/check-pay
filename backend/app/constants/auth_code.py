CODE_MIN_LENGTH = 2
CODE_MAX_LENGTH = 4

NUMBER_MIN_LENGTH = 8
NUMBER_MAX_LENGTH = 24

# 经过md5之后的密码字符串是32位
PASSWORD_MIN_LENGTH = 32
PASSWORD_MAX_LENGTH = 32

# 验证码长度
AUTH_CODE_LENGTH = 4

# 验证码过期时间
AUTH_CODE_EXPIRATION = 60 * 5

# 用户获取验证码的时间间隔
AUTH_CODE_GENERATE_INTERVAL = 60 * 1

# 每天可发送的短信验证码最大次数
AUTH_CODE_DAY_LIMIT_TIMES = 5

# token过期时间
TOKEN_EXPIRATION = 30 * 60
# 后台过去时间
TOKEN_EXPIRATION_ADMIN = 7 * 24 * 60 * 60

# 后台过去时间
TOKEN_EXPIRATION_MERCHANT = 12 * 60 * 60

# 测试 登陆成功后
TOKEN_MIN_LENGTH = 180
TOKEN_MAX_LENGTH = 240

# 短信验证码模版
SMS_CODE_MESSAGE_FORMAT = "【EPay】验证码{}，5分钟内有效。为保证账号安全，请勿告知任何人验证码。"
SMS_CODE_MESSAGE_FORMAT_YC_CN = "【壹Pay】您的验证码是{}"
SMS_CODE_MESSAGE_FORMAT_YC_EN = """【ecashier】Verification code {},valid within 5 minutes. For your protection,do not share the code with anyone"""

# 测试环境的万能验证码
SPECIAL_SMS_AUTH_CODE = "8888"

# 后台 登陆用户名最大长度
BACKOFFICE_USERNAME_MAX_LENGTH = 32

# 支付密码长度
PAYMENT_PASSWORD_LENGTH = 6


# 支付密码md5后长度
PAYMENT_PASSWORD_MD5_LENGTH = 32
