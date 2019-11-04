import fetch from '@/config/fetch'

/**
 * 登录
 */
export const login = data => fetch('/auth/account/login', data);
/**
 * 注册
 */
export const registern = data => fetch('/auth/account/register', data);
/**
 * 修改登录密码 
 */
export const passwordReset = data => fetch('/auth/password/reset', data);
/**
 * 退出
 */
export const signout = () => fetch('/auth/account/logout');





/*******************************
 * 
 *           商户管理           *
 * 
 *******************************/




/**
 * 商户列表
 */
export const merchantList = () => fetch('/merchant/list');
/**
 * 余额调整
 */
export const balanceEdit = date => fetch('/merchant/balance/edit', date);
/**
 * 获取商户配置信息
 */
export const configGetunt = () => fetch('/merchant/config/get');
/**
 * 新建商户
 */
export const feeAdd = data => fetch('/merchant/fee/add', data);
/**
 * 用户注册量
 */
export const feeEdit = date => fetch('/merchant/fee/edit', date);






/****************************************
 * 
 *           用户管理                    *
 * 
 ***************************************/






/**
 * 获取用户列表
 */
export const userManageuserList = data => fetch('/user_manage/user/list', data);
/**
 * 用户余额调整
 */
export const userManageBalanceEdit = data => fetch('/user_manage/user/balance/edit', data);
/**
 * 用户余额调整
 */
export const userManageUserDetail = data => fetch('/user_manage/user/detail', data);
/**
 * 删除用户银行卡
 */
export const userManageBankDelete = data => fetch('/user_manage/user/bank/delete', data);
/**
 * 用户最近一周充值提现交易记录
 */
export const userManageUserTransaction = data => fetch('/user_manage/user/transaction', data);






/****************************************
 * 
 *           通道管理                    *
 * 
 ***************************************/






/**
 * 充值通道列表
 */
export const depositList = () => fetch('/channel/deposit/list');
/**
 * 获取通道配置信息  {余额充值: 1, 余额提现: 2}
 */
export const channelConfigGet = data => fetch('/channel/config/get', data);
/**
 * 新建充值通道
 */
export const depositAdd = data => fetch('/channel/deposit/add', data);
/**
 * 编辑通道适用规则
 */
export const router2Update = data => fetch('/channel/router2/update', data);
/**
 * 编辑充值通道
 */
export const depositEdit = data => fetch('/channel/deposit/edit', data);
/**
 * 删除充值通道
 */
export const depositDel = data => fetch('/channel/deposit/del', data);
/**
 * 代付通道列表
 */
export const withdrawList = () => fetch('/channel/withdraw/list');
/**
 * 新建代付通道
 */
export const withdrawAdd = data => fetch('/channel/withdraw/add', data);
/**
 * 编辑代付通道
 */
export const withdrawEdit = data => fetch('/channel/withdraw/edit', data);
/**
 * 删除代付通道
 */
export const withdrawDel = data => fetch('/channel/withdraw/del', data);
/**
 * 引导规则列表
 */
export const ruleList = () => fetch('/channel/router/list');
/**
 * 新建引导规则
 */
export const ruleAdd = data => fetch('/channel/router/create', data);
/**
 * 编辑引导规则
 */
export const ruleEdit = data => fetch('/channel/router/update', data);







/****************************************
 * 
 *           交易管理                    *
 * 
 ***************************************/






/**
 * 充值订单列表
 */
export const depositOrderList = data => fetch('/trade_manage/deposit/order/list', data);
/**
 * 导出CSV：充值订单列表
 */
export const depositOrderListExport = data => fetch('/trade_manage/deposit/order/list/export', data);
/**
 * 充值订单详情
 */
export const depositOrderDetail = data => fetch('/trade_manage/deposit/order/detail', data);
/**
 * 充值订单人工补单配置信息
 */
export const depositConfigGet = () => fetch('/trade_manage/backoffice/config/get');
/**
 * 充值订单人工补单
 */
export const tradeOrderCreate = data => fetch('/trade_manage/deposit/order/create', data);
/**
 * 提现订单列表
 */
export const tradeWithdrawList = data => fetch('/trade_manage/withdraw/list', data);
/**
 * 获取待认领提现订单列表
 */
export const noTradeWithdrawListload = data => fetch('/trade_manage/withdraw/list', data, false);
/**
 * 导出CSV：提现订单列表
 */
export const tradeWithdrawListExport = data => fetch('/trade_manage/withdraw/list/export', data);
/**
 * 提现订单详情
 */
export const tradeOrderDetail = data => fetch('/trade_manage/withdraw/order/detail', data);
/**
 * 认领订单
 */
export const tradeOrderAllowed = data => fetch('/trade_manage/order/allowed', data);
/**
 * 审核列表
 */
export const tradeReviewList = data => fetch('/trade_manage/withdraw/review/list', data);
/**
 * 获取可用的代付通道
 */
export const tradeAvailableChannel = data => fetch('/trade_manage/withdraw/available/channel', data);
/**
 * 提交代付
 */
export const tradeWithdrawLaunch = data => fetch('/trade_manage/withdraw/launch', data);
/**
 * 获取人工出款银行卡信息
 */
export const tradeBankInfo = data => fetch('/trade_manage/withdraw/bank/info', data);
/**
 * 发起人工出款
 */
export const tradePersonExecute = data => fetch('/trade_manage/withdraw/person/execute', data);
/**
 * 人工出款完成
 */
export const tradePersonDone = data => fetch('/trade_manage/withdraw/person/done', data);
/**
 * 拒绝提现
 */
export const tradeRefuseReimburse = data => fetch('/trade_manage/withdraw/refuse/reimburse', data);
/**
 * 充值成功给商户发通知
 */
export const tradeRefuseOrderNotify = data => fetch('/trade_manage/order/notify', data);
/**
 * 人工完成充值订单
 */
export const tradeRefuseManuallyDone = data => fetch('/trade_manage/order/manually/done', data);