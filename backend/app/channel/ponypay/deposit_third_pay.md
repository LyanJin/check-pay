用户充值流程
1. 获取当前可用渠道，及单笔交易最高最低限制
2. 获取用户当前余额
3. 充值接口

    1. amount 充值金额
    2. 商户用户号
    3. 商户订单号（支付平台返回）
    4. 回调Url
    5. note 备注信息
    6. 用户存款银行
    7. bank_code 银行代码
    8. service_type
 
充值接口：
    前端参数：充值通道类型， 充值金额
    后台处理 发送预充值请求：    
        1. 向充值通道发送充值请求(充值金额，商户号， 商户订单号)
        2. 获取充值订单号
        3. 向前端发送 充值通道的充值页面url
    前端 获取充值面页面跳转 跳转成功后
    向后台发送 用户充值
    后台根据充值订单号 轮询订单 查看订单状态
    
    返回 充值通道提供的充值页面
    
    前端展示充值页面
    用户做充值动作

fields          field type        required       description
uid                int              必填            商户ID 
pay_type           int              必填            支付类型（1.微信  2.支付宝）
pay_id         string(24)           选填            指定支付账户   （如果不填写使用系统轮询策略分配）
group_id           int              选填            支付账户组ID   （如果不需要分组则填写0 如果需要指定多个分组ID请用逗号隔开,比如: 0,1,2,3,4,5）
goods_name     string(255)          选填            商品名称 
order_id       string(32)           选填            系统订单号      第三方订单号
price          float                必填            价格  
notify_url     string(255)          必填            回调url        通知url
exact          bool                 必填            是否使用精确金额支付  值为字符串”true”则为true，其余值都为false ，建议非精确支付
sign_type      string(5)            必填            签名算法  必填：sha1
sign           string(40)           签名            sha1(uid+pay_type+pay_id+group_id+goods_name+order_id+price+ notify_url+ exact+ sign_type+token)转换为小写Token可以从控制台获取



pay_type	    支付类型	    是	int	         支付类型固定为2，标记第三方支付
mch_id	        商户标识	    是	int	         商户id由我公司统一分配
order_id	    商户订单编号	是	string(32)	 商户系统中保持唯一
channel_id	    支付通道标识	是	int	         本次请求使用的支付方式
pay_amount	    支付金额	    是	decimal	     总金额，以元为单位，保留两位小数
name	        商品名	    是	string(64)	 商品名称
explain	        商品描述	    否	string(256)	 商品描述
remark	        订单备注	    否	string(256)	 订单的附加说明
result_url	    同步跳转地址	否	string(128)	"仅在wap类型的支付通道中有效，支付成功后页面跳转URL，GET跳转带有orderid和orderno参数,此页面仅用于展示，订单状态以notify_url通知为准"
notify_url	    异步通知地址	是	string(128)	"接收订单通知的URL，绝对路径如 http://api.rukoumy.com/callback 该地址必须为公网可以访问的地址"
client_ip	    客户端ip	    是	string(16)	 商家获取当前客户端ip发送给我公司
bank_cardtype	银行卡类型	否	string(10)	"仅在网银类型的支付通道中有效，非网银通道请留空 credit 表示信用卡 debit 表示借记卡"
bank_code	    网银编码	    否	string(4)	"仅在网银类型的支付通道中有效网银通道中不可为空,用于指定支付银行非网银通道请留空"
is_qrimg	    启用二维码图片	是	bool	    "仅在二维码类型的支付通道中有效
                                                0默认值,返回二维码JSON，商户自行展示
                                                1由我公司展示二维码
                                                 非二维码通道固定为0"
is_sdk	        是否直接拉起支付	是	bool	"仅在wap类型的支付通道中有效
                                                0默认值,标识是浏览器web请求
                                                1标识是直接拉起支付,接口返回包含原生支付地址code_url的JSON结果
                                                非wap通道固定为0"
ts	            时间戳	        是	long	Unix时间格式，如1473674315590
sign	        参数签名	        是	string(32)	MD5全参数签名，大写
ext	            附加信息	        否	string(256)	扩展参数，跟随响应原样返回


参数名	     描述	           必填	数据类型	     说明
code	    状态码	           是	int	         0为成功，其余均为失败，详见状态码说明
msg	        状态描述	           是	string(128)	 "code=0时返回success或空字符串其余返回状态说明"
ts	        时间戳	           是	long	      Unix时间格式，如1473674315590
sign	    参数签名	           是	string(32)	  code=0时有返回，MD5全参数签名，大写
pay_type	支付类型	           是	int	          支付类型固定为2，标记第三方支付
mch_id	    商户标识	           是	int	          商户id由我公司统一分配
order_id	商户订单编号	       是	string(32)	  商户系统中必须唯一
channel_id	支付通道标识	       是	int	          本次请求使用的支付方式
pay_amount	提交支付金额	       是	decimal	      "商户订单金额，以元为单位，保留两位小数第三方支付与real_amount一致"
real_amount	实际支付金额	       是	string(64)	  "订单成交金额，以元为单位，保留两位小数第三方支付与pay_amount一致"
status	    订单状态	           是	int	          "仅code=0且status=1时能确认支付成功 订单状态参见数据字典"
order_no	我公司订单号	       是	string(32)	  我公司的订单号
finish_time	订单操作完成时间	   是	datetime	  格式为yyyy-MM-dd HH24:mm:ss
ext	        附加信息	           否	string(256)	  扩展参数，跟随响应原样返回