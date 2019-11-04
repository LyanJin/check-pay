import fetch from '../config/fetch'


/******************************
 * 
 *            验证码模块
 * 
 *******************************/

/**
 * 获取验证码
 */
export const smsGet = data => fetch('/sms/get', data);
/**
 * 检验验证码是否正确
 */
export const smsVerify = data => fetch('/sms/verify', data);

/******************************
 * 
 *            用户注册登录
 * 
 *******************************/

/**
 * 检测手机号是否注册过
 */
export const numberCheck = data => fetch('/auth/mobile/check', data);
/**
 * 注册
 */
export const authRegister = data => fetch('/auth/account/register', data);
/**
 * 账号登录
 */
export const authLogin = data => fetch('/auth/account/login', data);
/**
 * 找回密码
 */
export const forgetPassw = data => fetch('/auth/password/forget/get', data);
/**
/**
 * 验证找回密码验证码*/
export const forgetVerify = data => fetch('/auth/password/forget/verify', data);
/**
 * 找回密码后重置密码
 */
export const forgetPasswReset = data => fetch('/auth/password/forget/set', data);
/**
 * 检查原密码是否正确
 */
export const resetVerify = data => fetch('/auth/password/reset/verify', data);
/**
 * 修改密码
 */
export const forgetChange = data => fetch('/auth/password/reset', data);


/******************************
 * 
 *            用户操作
 * 
 *******************************/

/**
 * 获取用户可用余额
 */
export const balanceGet = () => fetch('/user/balance/get');

/******************************
 *            订单列表
 *******************************/
/**
 * 获取用户(充值/提现)订单
 */
export const orderlist = data => fetch('/order/list', data, 'POST', false);


/******************************
 * 
 *            充值模块
 * 
 *******************************/

/**
 * 获取单笔交易最低最高限额
 */
export const limitConfigGet = () => fetch('/deposit/limit/config/get');
/**
 * 获取当前可用的充值方式
 */
export const paymentTypeList = data => fetch('/deposit/payment/type/list', data);
/**
 * 充值订单 创建预支付订单
 */
export const depositOrderCreate = data => fetch('/deposit/order/create', data);


/******************************
 * 
 *            提现模块
 * 
 *******************************/

/**
 * 获取单笔交易最低最高限额
 */
export const withdrawTypeList = () => fetch('/withdraw/limit/config/get');
/**
 * 获取当前可用的提现方式
 */
export const withdrawBanksList = () => fetch('/withdraw/banks/list');
/**
 * 创建用户提现订单
 */
export const withdrawOrderCreate = data => fetch('/withdraw/order/create', data);

/******************************
 * 
 *            用户设置
 * 
 *******************************/
/**
 * 设置支付密码
 */
export const newPaymentPassword = data => fetch('/setting/payment/password/set', data);
/**
 * 校验支付密码
 */
export const PaymentPasswordCheck = data => fetch('/setting/payment/password/check', data);
/**
 * 修改支付密码
 */
export const PaymentPasswordReset = data => fetch('/setting/payment/password/reset', data);
/**
 * 忘记支付密码，重置支付密码
 */
export const PaymentPasswordForgetSet = data => fetch('/setting/payment/password/forget/set', data);
/**
 * 获取用户的银行卡列表
 */
export const bankcardList = () => fetch('/setting/bankcard/list');
/**
 * 根据卡号获取银行卡归属地信息
 */
export const banklocationGet = data => fetch('/setting/bank/banklocation/get', data);
/**
 * 给用户添加银行卡
 */
export const bankcardAdd = data => fetch('/setting/bankcard/add', data);
/**
 * 删除用户银行卡
 */
export const bankcardDelete = data => fetch('/setting/bankcard/delete', data);


/******************************
 * 
 *            用户转账
 * 
 *******************************/

/**
 * 判断用户是否存在
 */
export const transferAccountQuery = data => fetch('/transfer/account/query', data);
/**
 * 用户转账
 */
export const transferTransfer = data => fetch('/transfer/transfer', data);
