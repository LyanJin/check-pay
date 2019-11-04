 paytype:
     WX:微信扫码，返回扫码跳转
     WXH5：微信wap
     ZFB：支付宝扫码，返回扫码跳转
     ZFBH5:支付宝wap
     YSF:云闪付
     YLNET：银联扫码
     YLNETH5：银联扫码wap
     NETGATE:网银支付
     QQ: QQ扫码
     QQH5：QQ扫码wap
     BAIDU:百度钱包
     BAIDUH5：百度钱包wap
     JD：京东支付
     JDH5：京东支付wap"


参数名称	参数含义	是否必填	参与签名	参数说明
merchant_id	商户号	是	是	平台分配商户号
orderid	订单号	是	是	上送订单号唯一, 字符长度20
paytype	支付方式	是	是	
notifyurl	服务端通知	是	是	服务端返回地址.（POST返回数据）
callbackurl	页面跳转通知	是	是	页面跳转返回地址（POST返回数据）
userip	客户IP地址	是	否	客服端的地址（微信必须使用，否则有安全限制不能付款）
money	订单金额	是	是	商品金额
sign	MD5签名	是	否	请看MD5签名字段格式