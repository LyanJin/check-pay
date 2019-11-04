import fetch from '@/config/fetch'

/**
 * 登录
 */
export const login = data => fetch('/auth/merchant/login', data);

/**
 * 退出
 */
export const signout = () => fetch('/auth/merchant/logout');

/**
 * 首页商户基本信息
 */
export const merchantIndex = () => fetch('/merchant_manage/merchant/Index');

/*******************************
 * 
 *           商户充值订单查询      *
 * 
 *******************************/
export const orderDeposit = date => fetch('/merchant_manage/select/order/deposit', date);
/**
 * 商户充值订单查询数据下载
 */
export const orderDepositCsv = date => fetch('/merchant_manage/select/order/deposit/csv', date);


/*******************************
 * 
 *           商户提现订单查询      *
 * 
 *******************************/
/**
 * 充值成功给商户发通知
 */
export const tradeRefuseOrderNotify = data => fetch('/merchant_manage/merchant/order/notify', data);
/**
 * 商户提现订单查询
 */
export const orderWithdraw = data => fetch('/merchant_manage/select/order/withdraw', data);
/**
 * 商户提现订单查询
 */
export const orderWithdrawCsv = data => fetch('/merchant_manage/select/order/withdraw/csv', data);