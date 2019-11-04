
##### 使用chrome浏览器，先安装JSONView插件
https://chrome.google.com/webstore/detail/jsonview/chklaanhfefbnpoihckbnefhakgolnmc?hl=zh-cn

##### 查询用户余额流水：
https://backoffice.epay1001.com/api/backoffice/v1/health/user/balance/events

?merchant=TEST&account=8618912341234

##### 查询用户余额：
https://backoffice.epay1001.com/api/backoffice/v1/health/query/user/balance

##### 查询商户余额流水：
https://backoffice.epay1001.com/api/backoffice/v1/health/merchant/balance/events

?merchant=TEST&date=20190815&export=1

查询日期：date=20190815

导出csv：export=1

不加这两个参数，默认查询当天的数据

##### 创建后台用户，如果已经创建就是修改密码：
https://backoffice.epay1001.com/api/backoffice/v1/health/register/admin

?account=panda

##### 创建商户后台用户，如果已经创建就是修改密码：
https://backoffice.epay1001.com/api/backoffice/v1/health/register/merchant

?merchant=TEST

##### 修改用户余额：
https://backoffice.epay1001.com/api/backoffice/v1/health/alter/balance

?account=8613812341234&balance=100

##### 通道配置查询：
https://backoffice.epay1001.com/api/backoffice/v1/health/channel/check

##### 查询商户配置：
查询商户域名/费率/通道等配置信息
https://backoffice.epay1001.com/api/backoffice/v1/health/merchant/check

##### 后台操作日志查询
https://backoffice.epay1001.com/api/backoffice/v1/health/admin/log

参数：account=panda&date=20190901&export=1

##### 订单修改日志
https://backoffice.epay1001.com/api/backoffice/v1/health/order/events

必填参数：merchant=test

可选参数：date=20190901&order_id=123&uid=123&ref_id=xxx&export=1

当不填写date时，默认查询当天所有的数据

##### 充值通道选择
https://backoffice.epay1001.com/api/backoffice/v1/health/deposit/channel/choice

##### 查询充值订单
https://backoffice.epay1001.com/api/backoffice/v1/health/deposit/order

##### 检查验证码发送次数
https://backoffice.epay1001.com/api/backoffice/v1/health/auth/code/check

##### 删除某个手机号码的短信发送次数限制
https://backoffice.epay1001.com/api/backoffice/v1/health/auth/code/clear

##### 查看登录密码次数
https://backoffice.epay1001.com/api/backoffice/v1/health/password/error/check

##### 删除登录密码错误次数限制
https://backoffice.epay1001.com/api/backoffice/v1/health/password/error/clear

##### 用户别名绑定
https://backoffice.epay1001.com/api/backoffice/v1/health/user/bind

##### 用户标签设置
https://backoffice.epay1001.com/api/backoffice/v1/health/user/flag/update

#### 用户权限控制
https://backoffice.epay1001.com/api/backoffice/v1/health/user/permission/update

##### docker负载均衡检查：
https://cashier-test.epay1001.com/api/cashier/v1/health/load/balance/check

##### 健康检查：
https://cashier-test.epay1001.com/api/cashier/v1/health/check

##### 热表清理检查
https://backoffice.epay1001.com/api/backoffice/v1/health/hot/table/check

#### 恢复交易ID状态
https://backoffice.epay1001.com/api/backoffice/v1/health/revoke/ref/id?tx_id=156618367063146100000
