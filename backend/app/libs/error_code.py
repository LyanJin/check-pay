"""
    错误码定义
"""
from app.libs.error_validator import ErrorCodeValidator
from app.libs.api_response import ResponseBase


############################################################
# 正常的业务逻辑响应
############################################################
class ResponseSuccess(ResponseBase):
    """
    没有异常，正常返回数据，大部分时候需要指定 data_model
    继承ResponseSuccess的类，不需要 ErrorCodeValidator.check() 的装饰
    """
    code = 200
    error_code = 200
    message = '请求成功'
    error_name = message


############################################################
# RESTFul api的错误码模型，结合实际情况使用
# 对 RESTFul 理解和使用不深刻，以及业务模型不适合时，不建议使用这些错误码
# 关于HTTP的 RESTFul Api状态码，参考：https://mccxj.github.io/blog/20130530_introduce-to-rest.html
############################################################
@ErrorCodeValidator.check()
class CreateSuccess(ResponseBase):
    """
    资源创建成功
    """
    code = 201
    error_code = code
    message = '资源创建成功'
    error_name = message


@ErrorCodeValidator.check()
class DeleteSuccess(ResponseBase):
    """
    资源删除成功
    """
    code = 202
    error_code = code
    message = '资源删除成功'
    error_name = message


@ErrorCodeValidator.check(True)
class AuthFailed(ResponseBase):
    code = 401
    error_code = code
    message = '鉴权失败'
    error_name = message


@ErrorCodeValidator.check(True)
class Forbidden(ResponseBase):
    code = 403
    error_code = code
    message = '没有权限，拒绝访问'
    error_name = message


@ErrorCodeValidator.check(True)
class NotFound(ResponseBase):
    code = 404
    error_code = code
    message = '未找到资源'
    error_name = message


@ErrorCodeValidator.check(True)
class RequestRateLimit(ResponseBase):
    code = 429
    error_code = code
    message = '您的操作过于频繁，请稍后重试'
    error_name = "请求频率限制"


@ErrorCodeValidator.check(True)
class ServerError(ResponseBase):
    code = 500
    error_code = code
    message = '系统异常，请稍后重试'
    error_name = message


############################################################
# 任何与客户端交互的业务逻辑错误，都使用 http code 400返回，
# 分别根据不同的业务逻辑定义不同的 error_code
############################################################

@ErrorCodeValidator.check(True)
class ParameterException(ResponseBase):
    """
    常用的异常类，在参数校验时使用，只要客户端传入的参数校验失败，抛出这个异常，结合wtform，可以给出很好的提示
    """
    code = 200
    error_code = 1000
    message = "具体的错误参数提示，如：手机号不能为空！"
    error_name = '参数错误'


########################################
# 商户费率配置检查
########################################
@ErrorCodeValidator.check()
class MerchantConfigDepositError(ResponseBase):
    code = 200
    error_code = 1004
    message = '请先配置商户充值费率'
    error_name = message


@ErrorCodeValidator.check()
class MerchantConfigWithdrawError(ResponseBase):
    code = 200
    error_code = 1005
    message = '请先配置商户提款费率'
    error_name = message


######################################################
# 获取手机验证码
######################################################
@ErrorCodeValidator.check()
class AuthCodeTimesLimitError(ResponseBase):
    code = 200
    error_code = 1007
    message = '当日验证码的发送次数已达上限'
    error_name = message


######################################################
# 验证码验证
######################################################
@ErrorCodeValidator.check()
class AuthCodeError(ResponseBase):
    code = 200
    error_code = 1009
    message = '验证码有误'
    error_name = message


@ErrorCodeValidator.check()
class AuthCodeExpiredError(ResponseBase):
    code = 200
    error_code = 1008
    message = '验证码已过期'
    error_name = message


@ErrorCodeValidator.check()
class AccountAlreadyExitError(ResponseBase):
    code = 200
    error_code = 1017
    message = '该用户已注册'
    error_name = message


###################################################
# 登陆错误
###################################################
@ErrorCodeValidator.check()
class AccountNotExistError(ResponseBase):
    code = 200
    error_code = 1018
    message = '账号不存在,请重新输入或注册新账号'
    error_name = message


@ErrorCodeValidator.check()
class LoginPasswordError(ResponseBase):
    code = 200
    error_code = 1019
    message = '账号或密码错误,请重新输入'
    error_name = message


@ErrorCodeValidator.check()
class MerchantLoginPasswordError(ResponseBase):
    code = 200
    error_code = 1015
    message = '账号或密码错误,请重新输入'
    error_name = message


@ErrorCodeValidator.check(login_default=True)
class LoginOtherError(AuthFailed):
    error_code = 1016
    message = '您的账号在其他地方（{}）登录，您被迫退出，如果不是您本人的操作，请注意账号安全！'
    error_name = "账号被异地登录了"


###################################################
# 测试用户登陆后 对受保护的其它接口操作
###################################################
@ErrorCodeValidator.check(login_default=True)
class TokenBadError(AuthFailed):
    error_code = 1020
    message = '无效的token'
    error_name = message


@ErrorCodeValidator.check(login_default=True)
class TokenExpiredError(AuthFailed):
    error_code = 1021
    message = 'token已过期'
    error_name = message


@ErrorCodeValidator.check()
class PasswordError(ResponseBase):
    code = 200
    error_code = 1022
    message = '原始密码错误'
    error_name = message


@ErrorCodeValidator.check()
class RePasswordError(ResponseBase):
    code = 200
    error_code = 1023
    message = '重置密码与原始密码一致'
    error_name = message


@ErrorCodeValidator.check()
class NoSourceError(ResponseBase):
    code = 200
    error_code = 1024
    message = '系统错误，找不到该用户'
    error_name = message


@ErrorCodeValidator.check()
class UserPermissionDeniedError(ResponseBase):
    code = 200
    error_code = 1025
    message = '权限拒绝'
    error_name = message


#####################################################
# backoffice 的错误码，从3000开始
# 登陆异常定义
#####################################################
@ErrorCodeValidator.check()
class MerchantUpdateError(ResponseBase):
    code = 200
    error_code = 3001
    message = '商户信息修改失败'
    error_name = message


@ErrorCodeValidator.check()
class UnauthorizedError(AuthFailed):
    error_code = 3002
    message = '未授权的请求'
    error_name = message


@ErrorCodeValidator.check()
class LoginAccountError(ResponseBase):
    code = 200
    error_code = 3003
    message = '用户名不存在'
    error_name = message


@ErrorCodeValidator.check()
class MerchantLoginAccountError(ResponseBase):
    code = 200
    error_code = 3004
    message = '商户尚未注册，请联系管理员'
    error_name = message


#############################################
# 密码输入错误次数达到上限
#############################################
@ErrorCodeValidator.check()
class OriPasswordError(AuthFailed):
    code = 401
    error_code = 3010
    message = '密码输入错误次数已达到上限(5次)，账户已锁定!'
    error_name = message


@ErrorCodeValidator.check()
class DisableUserError(AuthFailed):
    code = 401
    error_code = 3011
    message = '账户已锁定! 请通过忘记密码重置密码'
    error_name = message


##########################################################
# 商户管理
##########################################################

@ErrorCodeValidator.check()
class SqlIntegrityError(ResponseBase):
    code = 200
    error_code = 3012
    message = '该商户已存在 ! 请勿重复添加'
    error_name = message


##########################################################
# 通道管理
##########################################################

@ErrorCodeValidator.check()
class ChannelSqlIntegrityError(ResponseBase):
    code = 200
    error_code = 3013
    message = '该渠道已存在或优先级别已存在'
    error_name = message


@ErrorCodeValidator.check()
class DateStartMoreThanError(ResponseBase):
    code = 200
    error_code = 3014
    message = '起始时间必须小于终止时间'
    error_name = message


@ErrorCodeValidator.check()
class DataStartMoreThanError(ResponseBase):
    code = 200
    error_code = 3015
    message = '起始值必须小于最大值'
    error_name = message


@ErrorCodeValidator.check()
class MaintainDateError(ResponseBase):
    code = 200
    error_code = 3016
    message = '维护时间不能小于今天'
    error_name = message


@ErrorCodeValidator.check()
class NoSuchChannelError(ResponseBase):
    code = 200
    error_code = 3017
    message = '该实例尚未创建'
    error_name = message


@ErrorCodeValidator.check()
class PerLimitMustLittleDayLimitError(ResponseBase):
    code = 200
    error_code = 3018
    message = '单笔交易最大值必须小于当日交易限额'
    error_name = message


###################################################
# 用户充值错误
###################################################

@ErrorCodeValidator.check()
class NoSuchDataError(ResponseBase):
    code = 200
    error_code = 3200
    message = '数据异常'
    error_name = message


@ErrorCodeValidator.check()
class OperateCacheError(ResponseBase):
    code = 200
    error_code = 3201
    message = '操作缓存异常'
    error_name = message


@ErrorCodeValidator.check()
class DepositOrderAmountInvalidError(ResponseBase):
    code = 200
    error_code = 3206
    message = '充值金额不在有效范围内'
    error_name = message


###################################################
# 设置支付密码相关的错误
###################################################

@ErrorCodeValidator.check()
class PaymentPwdExistError(ResponseBase):
    code = 200
    error_code = 4000
    message = '交易密码已经存在'
    error_name = message


@ErrorCodeValidator.check()
class PaymentPasswordError(ResponseBase):
    code = 200
    error_code = 4001
    message = '支付密码错误，还有{}次机会'
    error_name = '交易密码错误'


@ErrorCodeValidator.check()
class PaymentPasswordLimitedError(ResponseBase):
    code = 200
    error_code = 4002
    message = '交易密码输入错误次数已达到上限(5次)!'
    error_name = message


@ErrorCodeValidator.check()
class PaymentPwdNotExistError(ResponseBase):
    code = 200
    error_code = 4003
    message = '交易密码不存在'
    error_name = message


@ErrorCodeValidator.check()
class PaymentPwdResetSameError(ResponseBase):
    code = 200
    error_code = 4004
    message = '新支付密码不能跟老支付密码相同'
    error_name = message


###################################################
# 用户银行卡相关的错误码
###################################################

@ErrorCodeValidator.check()
class BankCardNumLimitedError(ResponseBase):
    code = 200
    error_code = 4100
    message = '最多只能添加8张银行卡'
    error_name = message


@ErrorCodeValidator.check()
class BankCardExistError(ResponseBase):
    code = 200
    error_code = 4102
    message = '该银行卡已经被绑定过了'
    error_name = message


@ErrorCodeValidator.check()
class BankCardAccountNameError(ResponseBase):
    code = 200
    error_code = 4101
    message = '开户名必须跟第一次绑卡的开户名相同'
    error_name = message


@ErrorCodeValidator.check()
class BankCardNotExistError(ResponseBase):
    code = 200
    error_code = 4103
    message = '银行卡不存在'
    error_name = message


@ErrorCodeValidator.check()
class BankCardNotMeError(ResponseBase):
    code = 200
    error_code = 4104
    message = '只能删除自己的银行卡'
    error_name = message


###################################################
# 用户转账相关的错误码
###################################################
@ErrorCodeValidator.check()
class TransferToMeError(ResponseBase):
    code = 200
    error_code = 4200
    message = '不能给自己转账'
    error_name = message


@ErrorCodeValidator.check()
class InvalidBankNumber(ResponseBase):
    code = 200
    error_code = 4005
    message = '无效的银行卡号'
    error_name = message


@ErrorCodeValidator.check()
class InvalidDepositChannelError(ResponseBase):
    code = 200
    error_code = 3202
    message = '找不到有效的充值通道'
    error_name = message


@ErrorCodeValidator.check()
class PreOrderCreateError(ResponseBase):
    code = 200
    error_code = 3203
    message = '充值失败，请联系在线客服'
    error_name = message


@ErrorCodeValidator.check()
class InvalidDepositPaymentTypeError(ResponseBase):
    code = 200
    error_code = 3204
    message = '无效的支付类型'
    error_name = message


@ErrorCodeValidator.check()
class ChannelNoValidityPeriodError(ResponseBase):
    code = 200
    error_code = 3205
    message = '该支付通道不再交易日期内'
    error_name = message


@ErrorCodeValidator.check()
class MustRequestDepositLimitError(ResponseBase):
    code = 200
    error_code = 3207
    message = '请首先获取充值上限'
    error_name = message


####################################################
# 充值回调
####################################################

@ErrorCodeValidator.check()
class DepositCallbackIpNotInWhiteError(ResponseBase):
    code = 200
    error_code = 3300
    message = '回调请求ip不在白名单内'
    error_name = message


@ErrorCodeValidator.check()
class DepositCallbackSignError(ResponseBase):
    code = 200
    error_code = 3301
    message = '回调签名失败'
    error_name = message


@ErrorCodeValidator.check()
class DepositCallbackUserBalanceError(ResponseBase):
    code = 200
    error_code = 3302
    message = ''
    error_name = message


@ErrorCodeValidator.check()
class DepositCallbackOrderStatusError(ResponseBase):
    code = 200
    error_code = 3303
    message = '订单状态更新失败'
    error_name = message


@ErrorCodeValidator.check()
class DepositCallbackNofoundOrderError(ResponseBase):
    code = 200
    error_code = 3304
    message = '查询该订单失败'
    error_name = message


@ErrorCodeValidator.check()
class DepositCallbackOrderCompleteError(ResponseBase):
    code = 200
    error_code = 3305
    message = '该订单已处理'
    error_name = message


################################################################
################################################################
@ErrorCodeValidator.check()
class WithdrawOrderAmountInvalidError(ResponseBase):
    code = 200
    error_code = 3400
    message = '提现金额不在有效范围内'
    error_name = message


@ErrorCodeValidator.check()
class AccountBalanceInsufficientError(ResponseBase):
    code = 200
    error_code = 3401
    message = '账户余额不足'
    error_name = message


@ErrorCodeValidator.check()
class WithdrawOrderCreateError(ResponseBase):
    code = 200
    error_code = 3402
    message = '提现订单创建失败'
    error_name = message


@ErrorCodeValidator.check()
class WithdrawBankNoExistError(ResponseBase):
    code = 200
    error_code = 3403
    message = '银行卡信息有误，请检查该银行卡是否存在'
    error_name = message


#####################################################
# 钱包端 订单查询
#####################################################

@ErrorCodeValidator.check()
class SelectDepositWithdrawDateError(ResponseBase):
    code = 200
    error_code = 3500
    message = '选择的日期错误'
    error_name = message


@ErrorCodeValidator.check()
class SelectDepositWithdrawPageParamsError(ResponseBase):
    code = 200
    error_code = 3501
    message = '单页条数和页码数必须为有效的整数'
    error_name = message


##############################################################
# 交易管理： 提现管理： 提现订单认领
##############################################################

@ErrorCodeValidator.check()
class NoSuchWithdrawOrderError(ResponseBase):
    code = 200
    error_code = 3600
    message = '提现订单查询失败'
    error_name = message


@ErrorCodeValidator.check()
class NoSuchOpeUserError(ResponseBase):
    code = 200
    error_code = 3601
    message = '当前用户不能做认领'
    error_name = message


@ErrorCodeValidator.check()
class DoNotAllowedOrderError(ResponseBase):
    code = 200
    error_code = 3602
    message = '当前订单已被认领，请勿重复认领'
    error_name = message


@ErrorCodeValidator.check()
class AllowedOrderError(ResponseBase):
    code = 200
    error_code = 3603
    message = '当前订单认领失败'
    error_name = message


@ErrorCodeValidator.check()
class NotAllocOrderError(ResponseBase):
    code = 200
    error_code = 3604
    message = '不能对未经分配的订单进行出款'
    error_name = message


@ErrorCodeValidator.check()
class InvalidChannelError(ResponseBase):
    code = 200
    error_code = 3605
    message = '无效的通道ID'
    error_name = message


@ErrorCodeValidator.check()
class FailedLaunchWithdrawError(ResponseBase):
    code = 200
    error_code = 3606
    message = '提款请求失败'
    error_name = message


@ErrorCodeValidator.check()
class WithdrawUpdateDealingError(ResponseBase):
    code = 200
    error_code = 3607
    message = '更新订单状态为处理中失败'
    error_name = message


@ErrorCodeValidator.check()
class BankOrderStateError(ResponseBase):
    code = 200
    error_code = 3608
    message = '当前订单不可操作'
    error_name = message


@ErrorCodeValidator.check()
class BankInfoMissingError(ResponseBase):
    code = 200
    error_code = 3609
    message = '用户提现信息缺失'
    error_name = message


@ErrorCodeValidator.check()
class OrderInfoMissingError(ResponseBase):
    code = 200
    error_code = 3610
    message = '查不到该订单'
    error_name = message


@ErrorCodeValidator.check()
class WithdrawOrderStateChangeError(ResponseBase):
    code = 200
    error_code = 3611
    message = '提现订单状态跟新失败'
    error_name = message


@ErrorCodeValidator.check()
class NosuchOrderDetailDataError(ResponseBase):
    code = 200
    error_code = 3612
    message = '找不到对应的详情表'
    error_name = message


@ErrorCodeValidator.check()
class WithdrawFeeEmptyError(ResponseBase):
    code = 200
    error_code = 3613
    message = '用户提现手续费不能为空'
    error_name = message


@ErrorCodeValidator.check()
class MultiMonthQueryError(ResponseBase):
    code = 200
    error_code = 3620
    message = '查询开始时间和结束时间只能在同一个自然月的周期内'
    error_name = message


##############################################################
# gateway API错误码
##############################################################
@ErrorCodeValidator.check()
class GatewayIPError(ResponseBase):
    code = 200
    error_code = 10000
    message = 'IP不在白名单内'
    error_name = message
    doc_path = False


@ErrorCodeValidator.check()
class GatewaySignError(ResponseBase):
    code = 200
    error_code = 10001
    message = '签名校验失败'
    error_name = message
    doc_path = False


@ErrorCodeValidator.check()
class GatewayChannelError(ResponseBase):
    code = 200
    error_code = 10002
    message = '无可用通道，请确认输入金额是否在有效范围内'
    error_name = message
    doc_path = False


@ErrorCodeValidator.check()
class GatewayDepositError(ResponseBase):
    code = 200
    error_code = 10003
    message = '充值发起失败'
    error_name = message
    doc_path = False


@ErrorCodeValidator.check()
class GatewayWithdrawError(ResponseBase):
    code = 200
    error_code = 10004
    message = '提现发起失败'
    error_name = message
    doc_path = False


#####################################################
# merchant office
#####################################################

@ErrorCodeValidator.check()
class MerchantInfoNoExistError(ResponseBase):
    code = 200
    error_code = 20001
    message = '商户信息不存在，请与管理员联系'
    error_name = message
    doc_path = False


######################################################
# 用户管理
######################################################

@ErrorCodeValidator.check()
class AdjustUserBalanceError(ResponseBase):
    code = 200
    error_code = 3700
    message = ''
    error_name = message


@ErrorCodeValidator.check()
class UserBalanceNoFoundError(ResponseBase):
    code = 200
    error_code = 3701
    message = '用户余额数据缺失'
    error_name = message


@ErrorCodeValidator.check()
class InvalidOrderIdError(ResponseBase):
    code = 200
    error_code = 3702
    message = '无效的订单号'
    error_name = message
