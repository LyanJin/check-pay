"""
通道提供商配置
"""
import os
from app.enums.trade import ZYFBANKS
from app.enums.base_enum import BaseEnum
from config import MerchantDomainConfig


class ThirdPayConfig(BaseEnum):
    LIMAFU_95632 = dict(
        provider='立马付',
        # 第三放分配给我们的商户ID
        mch_id='95632',
        # 密钥，先从环境变量读取，赌不到再用默认的
        secret_key=os.getenv(
            'SECRET_KEY_LIMAFU') or "2490781216072527417564519496293743607070780739173751307932725890",
        white_ip=[
            "47.75.97.70", "47.244.106.140", "47.75.147.108", "47.75.44.112",
            "47.75.97.70", "47.244.106.140", "47.75.147.108", "47.75.44.112", "47.90.101.181", "47.244.21.231",
            "47.52.126.10",
            "114.198.145.117", "127.0.0.1"
        ],

        # 充值配置
        post_url="http://api.ponypay1.com/",
        callback_url="https://{}/api/callback/v1/callback/ponypay/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        request_cls="app.channel.ponypay.deposit.request.DepositRequest",

        # 提款配置
        withdraw_path="payforcustom.aspx",
        withdraw_cb_url="https://{}/api/callback/v1/callback/ponypay/withdraw".format(
            MerchantDomainConfig.get_callback_domain()),
        withdraw_cls="app.channel.ponypay.withdraw.request.WithdrawRequest",
        server_ip="114.198.145.117",  # 代付提交请求需要提供本侧服务器IP地址
    )

    # 极付，充值
    JIFU = dict(
        provider='极付',
        # 第三放分配给我们的商户ID
        mch_id='ed86abd745e45dfd',  # 没有商户ID，使用app ID代替
        app_id="ed86abd745e45dfd",
        # 密钥，先从环境变量读取，赌不到再用默认的
        secret_key=os.getenv('SECRET_KEY_JIFU') or "0bc6e30aed86abd745e45dfd78c67ff1",
        white_ip=[
            "47.52.64.93",
            # 自己的测试IP
            "18.162.236.151",
            "18.162.143.27",
            "18.162.123.175",
        ],

        # 充值配置
        post_url="https://sdk.geekpay.top/v2/app/createOrder",
        callback_url="https://{}/api/callback/v1/callback/jifu/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        request_cls="app.channel.jifu.deposit.request.DepositRequest",
    )

    ZHUANYIFU_11159 = dict(
        provider='专一付',
        # 第三放分配给我们的商户ID
        mch_id='11159',
        app_id='11153',
        white_ip=[],
        # 回调配置
        post_url="https://pay.zhuanyifu.com/",
        withdraw_path="gateway",
        withdraw_cb_url="https://{}/api/callback/v1/callback/zhuanyifu/withdraw".format(
            MerchantDomainConfig.get_callback_domain()),
        withdraw_cls="app.channel.zhuanyifu.withdraw.request.RequestZhuanYiFu",
        # 密钥，用户做签名
        secret_key="xiZgYsxagQWmtW2cNPA2L9hZ299jGa7wpEiL2SV75OA=",
        # 第三方公钥，收到响应了用于解密
        plat_public_key="""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCaB+w+RfL0iuRJT9y0+bgfi8jm
atTpQY74vvLmtNa45Yaq2+rs7FdAyVomRralll411kKuYaCqNB3mIUGTT3tCq+c0
PIkXk+aAPlUgehRy3FozcFuzO1i6ofq1xs+rJg5XtodX7G+A3rmpUMJ2vexv68rR
ovBvJKxRkDJsG7BvbQIDAQAB
""",
        # 商户私钥，发起请求时，用于加密
        mch_private_key="""-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCfFoMUKn3Yy+ChSD6LfeG7E9qlvS+IuUYvSZ35ShgZnW+oECcm
a/TgpuOU1G6BUogy5lkfFPKUm8/GEy6exAx1z5YtsfZdp51hSrJRPjkz2QdpQVNC
AIxhO45J7wqB04PU2CuCcKOX3zqwfyrEVA54spqWPMvcpf1FB6xrYm+OuwIDAQAB
AoGAIaNvdPilIo29gizV+MXV0KpajbgKkIToh8AvtJILtYLaJLXBqXijT0tKjOI8
OYEbhnO5fX5+6phlnxLYRT7cCUkCTwkI/qH2oqgy3hrDyYSm+aGZTmIOQO3dRYfB
uu7iweOUbbD3EvZuljmr7vbFNhdYvTDiUD0M/hk2QzFDScECQQDnsV/79u1TNSzz
u3v838dKlfHXUKf1q/NcSP23avH0FqrTF2Jo5PL89ZR2T8Ldw3XFaJJ4BY06yhwO
8A8xWeRBAkEAr8crvGhbe5zVfUKDrpYrdL8Rx4aDjaGgwYPXsY3xmyJ6mvgAyKug
bnwcuPs2UioTRlWYLzrEOLdPK+t9CaAD+wJBALRab3QMX+sgfpBvxfEvJMwbcnj/
8O6c3kBdFRrc5eDycCEHl/Q9HCTq6Zk7N143E4sKftFsyOYVg8fg+IKbDcECQCcU
xlGWdjiOjxzRbAumEbVcQey1qIwV0nMUCCHO6FfQm6fW2f3DwuCtsYkjOVmdRznN
EA/4JeZiQzUFn4BDVn8CQFSl2hv0bB/HIdu/g/jCHMebpXwJTcV+UFvkuWkQkqX5
yjVLFNJ+yzhmAyXOOly8gNKYLcwT+6jmMDLa2a3+1nU=
-----END RSA PRIVATE KEY-----""",
        banks=ZYFBANKS
    )

    ZHUANYIFU_DEPOSIT_11159 = dict(
        provider='专一付',
        # 第三放分配给我们的商户ID
        mch_id='11159',
        app_id='11158',
        white_ip=[],
        # 回调配置
        post_url="https://pay.zhuanyifu.com/",
        withdraw_path="gateway",
        request_cls="app.channel.zhuanyifu.deposit.request.DepositRequest",
        withdraw_cb_url="https://{}/api/callback/v1/callback/zhuanyifu/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        withdraw_cls="app.channel.zhuanyifu.deposit.request.RequestZhuanYiFu",
        # 密钥，用户做签名
        secret_key="xiZgYsxagQWmtW2cNPA2L9hZ299jGa7wpEiL2SV75OA=",
        # 第三方公钥，收到响应了用于解密
        plat_public_key="""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCaB+w+RfL0iuRJT9y0+bgfi8jm
atTpQY74vvLmtNa45Yaq2+rs7FdAyVomRralll411kKuYaCqNB3mIUGTT3tCq+c0
PIkXk+aAPlUgehRy3FozcFuzO1i6ofq1xs+rJg5XtodX7G+A3rmpUMJ2vexv68rR
ovBvJKxRkDJsG7BvbQIDAQAB""",
        # 商户私钥，发起请求时，用于加密
        mch_private_key="""-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQCF2Urdg0lS5SyQVPWCz7dWAgBFhZ32QAAIBIrPzduY2ADgAkOv
PdQUTQ0E1OJWXL5MXVd8eb+eVo6N72fCQMhbOHFF4YLu2EtURQCUkRK+d5y/t1U+
JXWtkZkSP10mrKnZeKiVXLyohJrRai+VB44sPmhAsjXTDuNb4bIw5cWAcQIDAQAB
AoGACVolBxx33HcHEbgf9eGD1Lp70J+9CWJQJj9EADBI6FFqYTyDRGywY3E9SEHE
JUbiZIVOmjPLCdoQKJZqVGownYWit4Lj/inRHBaN81lKmyWf2RgIBZeyLwmfh/H7
XEdJ5G7W8R7Sp+oWR7oYILekXZ483F+xdvCOAHPsVphzTIkCQQDj4GENGKVUtQ2P
I5fgLqx4pQCt2Iyx4FrSsR31HYEvnrAqUn3V3fJqu1+DtXvXGdVh1pNHYNdWMTjz
x2MCf3h5AkEAll4qQHlZzN1GZpYnGl+z3ZQIa5aj+t/Bffl74cyiLLfgjXCoCu6h
mRUwF5Wbjb4kOBTHBrMYzjAc6OIlEFi5uQJACyXA2ako/VnWDfiJx3fBDC3WOKrt
Rw5YoxHzCzikRzYWHBvo9/thjoMYCxNnuYAUBjM/BTDhl9/Uj2hjmY2u0QJAMQPi
+/9SoXAjyb76YiN+KyVdFU0WiOm1Vg4kLreYycDqptBpRp8A+Diq45U2Dp9DiTBk
rC9nT5bpZZSKBmkVqQJAQ50u9grPK3+aSAYRUhuB/LOnAYMc+AhdVLJ1ZMInhTXP
nunLfHMTOGBckUg2iiUFXXH/kdwdO9J79k259OC8mA==
-----END RSA PRIVATE KEY-----"""
    )

    KUAIHUI = dict(
        provider='快汇支付',
        # 第三放分配给我们的商户ID
        custid='PAY5f34c380-b8e6-11e9-9edc-511803f475f9',
        mch_id='PAY5f34c380-b8e6-11e9-9edc-511803f475f9',
        white_ip=['18.136.94.156', '13.228.84.45', "127.0.0.1"],
        # 充值配置
        apiUrl="https://api.khpay666.com",
        callback_url="https://{}/api/callback/v1/callback/kuaihui/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        request_cls="app.channel.kuaihui.deposit.request.DepositRequest",

        # 密钥，先从环境变量读取，读不到再用默认的
        secret_key=os.getenv(
            'SECRET_KEY_KUAIHUI') or "DWfEg3kuebnju7Y7xhnuJdk1pPoavbFL",
    )
    KUAIHUI_0bd0d8 = dict(
        provider='快汇支付2',
        # 第三放分配给我们的商户ID
        custid='PAY7a95a860-df5b-11e9-8e00-19ab8a0bd0d8',
        mch_id='PAY7a95a860-df5b-11e9-8e00-19ab8a0bd0d8',
        white_ip=['18.136.94.156', '13.228.84.45', "127.0.0.1"],
        # 充值配置
        apiUrl="https://api.khpay666.com",
        callback_url="https://{}/api/callback/v1/callback/kuaihui/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        request_cls="app.channel.kuaihui.deposit.request.DepositRequest",

        # 密钥，先从环境变量读取，读不到再用默认的
        secret_key=os.getenv(
            'SECRET_KEY_KUAIHUI') or "R8Za6VYhP7Tyj0R8wIHipbZNuIB3aiSC",
    )
    YINSAO_DEPOSIT = dict(
        provider='银扫支付',
        mch_id='81014799126367',
        secret_key=os.getenv(
            'SECRET_KEY_YINSAO') or "4714d9d7b8cbb910f6b9be08b7482cd5",
        post_url="http://47.112.103.35:8167/api",
        deposit_path='/payment/trade',
        request_cls="app.channel.yinsao.deposit.request.DepositYinSaoRequest",
        callback_url="https://{}/api/callback/v1/callback/yinsao/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        white_ip=[
            "47.112.103.35", "127.0.0.1", "114.198.145.117", "10.255.0.3"]
    )
    YINSAO_WITHDRAW = dict(
        provider='银扫支付',
        mch_id='81014799126367',
        secret_key=os.getenv(
            'SECRET_KEY_YINSAO') or "4714d9d7b8cbb910f6b9be08b7482cd5",
        post_url="http://47.112.103.35:8167/api",
        withdraw_path='/payment/pay',
        withdraw_cls="app.channel.yinsao.withdraw.request.WithdrawRequest",
        callback_url="https://{}/api/callback/v1/callback/yinsao/withdraw".format(
            MerchantDomainConfig.get_callback_domain()),
        white_ip=[
            "47.112.103.35", "127.0.0.1", "114.198.145.117", "10.255.0.3"]
    )
    ONE_PAY_DEPOSIT = dict(
        provider='易付银联',
        # HMCP-CNY-5919
        mch_id='5919',
        secret_key=os.getenv(
            'SECRET_KEY_YINSAO') or "4714d9d7b8cbb910f6b9be08b7482cd5",
        post_url="https://api.onepay.solutions/payment/v3",
        deposit_path='/checkOut.html',
        request_cls="app.channel.onepay.deposit.request.RequestOnePay",
        # callback_url="https://callback.epay1001.com/api/callback/v1/callback/onepay/deposit",
        callback_url="https://{}/api/callback/v1/callback/onepay/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        result_url="https://{}/api/callback/v1/callback/onepay/result".format(
            MerchantDomainConfig.get_callback_domain()),
        white_ip=[
            "47.112.103.35", '127.0.0.1', '52.77.54.169', '13.251.80.73'],
        plat_private_key="""-----BEGIN RSA PRIVATE KEY-----
        MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAI3m2ciUgpfxi73yBN8fmyyniBroLoolFO8+rxI1gSZ7Ve26j3QWKa9htigDAC/1F3fWm6foFB57WvdpTzm5nRdnLrKIab3M8t4Iv0fxbvMnasrVflyC7Ezp2Tzs1KM1m2IGnYC2hlh4469YS9N4H1Yu+j9j8B32GyRZBS0GnfbNAgMBAAECgYAJTUCpbVLCMws+AEdheOjrHHBHk0C5vYSJykofn3I/24Xed4Q/z9QbswQFy2yPuDk5mc/KSeRHuz5TSYvv9MLfVE/KMTLSsFWB9qrVayQnADc19OkkdyBx05kz+XrZyu497yU3T/HXMMhxxmWQvBe4lr4ZwKR6BKnLAzxOVzFT4QJBAOt5UgwAMIZ0IMBcA0L+jAUdldZbGVp6QYtr/7cBx06DN9gc3aEt+tub2f4w+UuCcaTfk9Hk0E9ZC5kMxg9zywMCQQCaRW+upWMiuqtlLpXYTAtXzRPbb+7DFnT12AzmwfqLj8VFrJZhjVVaj6qEGIU4BuxCMnoQ9TctcYzFQT8wZCXvAkBgnoA+8lj24nGJ3HduJto3QyN3OBwYFvAMED11zyIDoi3o3DdIaoBzWejBt0CjbhvJZf/WcQfUdxoeK7KdJosXAkAf4S92ELlOyPJ4Q0s12mkRqNBsrVHSwMZEs3PfD8DdrEUg48xjtlgoEb4z8/k7nbqe511wOaxAWNG1RYlwT5HDAkEA2Kjjjc59whpfzqthq0Ugjh+SqvUalMvI4CrNzog/i+gMne4NO9yuYQExC7s3OWor+ud8QQAAujAriJcQFAjVIQ==
        -----END RSA PRIVATE KEY-----""",
        plat_public_key="""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbBfTg5fedJ372LIyMdzu55Nnb7CtS9bbllkDBohX9K4keYE9JdF1bfrqvbjlPA558/jmxNbVJn2/x1OydS4gJZf7FPoeqzTPvc2PN8+H1/iO27sN5z7I65QBkHy80dV9au6wf5OHXjcU1Ls6S1bh5xqSRlKRreL6V6uLKuGRetwIDAQAB"""
    )

    ONE_PAY_QR_DEPOSIT = dict(
        provider='易付银联',
        # HMCP-CNY-5919
        mch_id='5919',
        secret_key=os.getenv(
            'SECRET_KEY_YINSAO') or "4714d9d7b8cbb910f6b9be08b7482cd5",
        post_url="https://api.onepay.solutions/payment/otoSoft/v3",
        deposit_path='/getQrCode.html',
        request_cls="app.channel.onepay.deposit.request.RequestQROnePay",
        # callback_url="https://callback.epay1001.com/api/callback/v1/callback/onepay/cashier_deposit",
        callback_url="https://{}/api/callback/v1/callback/onepay/cashier_deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        result_url="https://{}/api/callback/v1/callback/onepay/result".format(
            MerchantDomainConfig.get_callback_domain()),
        white_ip=[
            "47.112.103.35", '127.0.0.1', '52.77.54.169', '13.251.80.73'],
        plat_private_key="""-----BEGIN RSA PRIVATE KEY-----
            MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAI3m2ciUgpfxi73yBN8fmyyniBroLoolFO8+rxI1gSZ7Ve26j3QWKa9htigDAC/1F3fWm6foFB57WvdpTzm5nRdnLrKIab3M8t4Iv0fxbvMnasrVflyC7Ezp2Tzs1KM1m2IGnYC2hlh4469YS9N4H1Yu+j9j8B32GyRZBS0GnfbNAgMBAAECgYAJTUCpbVLCMws+AEdheOjrHHBHk0C5vYSJykofn3I/24Xed4Q/z9QbswQFy2yPuDk5mc/KSeRHuz5TSYvv9MLfVE/KMTLSsFWB9qrVayQnADc19OkkdyBx05kz+XrZyu497yU3T/HXMMhxxmWQvBe4lr4ZwKR6BKnLAzxOVzFT4QJBAOt5UgwAMIZ0IMBcA0L+jAUdldZbGVp6QYtr/7cBx06DN9gc3aEt+tub2f4w+UuCcaTfk9Hk0E9ZC5kMxg9zywMCQQCaRW+upWMiuqtlLpXYTAtXzRPbb+7DFnT12AzmwfqLj8VFrJZhjVVaj6qEGIU4BuxCMnoQ9TctcYzFQT8wZCXvAkBgnoA+8lj24nGJ3HduJto3QyN3OBwYFvAMED11zyIDoi3o3DdIaoBzWejBt0CjbhvJZf/WcQfUdxoeK7KdJosXAkAf4S92ELlOyPJ4Q0s12mkRqNBsrVHSwMZEs3PfD8DdrEUg48xjtlgoEb4z8/k7nbqe511wOaxAWNG1RYlwT5HDAkEA2Kjjjc59whpfzqthq0Ugjh+SqvUalMvI4CrNzog/i+gMne4NO9yuYQExC7s3OWor+ud8QQAAujAriJcQFAjVIQ==
            -----END RSA PRIVATE KEY-----""",
        plat_public_key="""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbBfTg5fedJ372LIyMdzu55Nnb7CtS9bbllkDBohX9K4keYE9JdF1bfrqvbjlPA558/jmxNbVJn2/x1OydS4gJZf7FPoeqzTPvc2PN8+H1/iO27sN5z7I65QBkHy80dV9au6wf5OHXjcU1Ls6S1bh5xqSRlKRreL6V6uLKuGRetwIDAQAB"""
    )

    ONE_PAY_WITHDRAW = dict(
        provider='易付银联',
        # HMCP-CNY-5919
        mch_id='5919',
        secret_key=os.getenv(
            'SECRET_KEY_ONEPAY') or "4714d9d7b8cbb910f6b9be08b7482cd5",
        post_url="https://api.onepay.solutions/v2/distribute",
        withdraw_path='/withdraw.html',
        withdraw_cls="app.channel.onepay.withdraw.request.WithdrawRequest",
        callback_url="https://{}/api/callback/v1/callback/onepay/withdraw".format(
            MerchantDomainConfig.get_callback_domain()),
        # result_url="https://callback.epay1001.com/api/callback/v1/callback/onepay/result",
        white_ip=[
            "47.112.103.35", '52.77.54.169', '13.251.80.73', '103.119.131.7', '127.0.0.1'],
        plat_private_key="""-----BEGIN RSA PRIVATE KEY-----
                MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAI3m2ciUgpfxi73yBN8fmyyniBroLoolFO8+rxI1gSZ7Ve26j3QWKa9htigDAC/1F3fWm6foFB57WvdpTzm5nRdnLrKIab3M8t4Iv0fxbvMnasrVflyC7Ezp2Tzs1KM1m2IGnYC2hlh4469YS9N4H1Yu+j9j8B32GyRZBS0GnfbNAgMBAAECgYAJTUCpbVLCMws+AEdheOjrHHBHk0C5vYSJykofn3I/24Xed4Q/z9QbswQFy2yPuDk5mc/KSeRHuz5TSYvv9MLfVE/KMTLSsFWB9qrVayQnADc19OkkdyBx05kz+XrZyu497yU3T/HXMMhxxmWQvBe4lr4ZwKR6BKnLAzxOVzFT4QJBAOt5UgwAMIZ0IMBcA0L+jAUdldZbGVp6QYtr/7cBx06DN9gc3aEt+tub2f4w+UuCcaTfk9Hk0E9ZC5kMxg9zywMCQQCaRW+upWMiuqtlLpXYTAtXzRPbb+7DFnT12AzmwfqLj8VFrJZhjVVaj6qEGIU4BuxCMnoQ9TctcYzFQT8wZCXvAkBgnoA+8lj24nGJ3HduJto3QyN3OBwYFvAMED11zyIDoi3o3DdIaoBzWejBt0CjbhvJZf/WcQfUdxoeK7KdJosXAkAf4S92ELlOyPJ4Q0s12mkRqNBsrVHSwMZEs3PfD8DdrEUg48xjtlgoEb4z8/k7nbqe511wOaxAWNG1RYlwT5HDAkEA2Kjjjc59whpfzqthq0Ugjh+SqvUalMvI4CrNzog/i+gMne4NO9yuYQExC7s3OWor+ud8QQAAujAriJcQFAjVIQ==
                -----END RSA PRIVATE KEY-----""",
        plat_public_key="""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbBfTg5fedJ372LIyMdzu55Nnb7CtS9bbllkDBohX9K4keYE9JdF1bfrqvbjlPA558/jmxNbVJn2/x1OydS4gJZf7FPoeqzTPvc2PN8+H1/iO27sN5z7I65QBkHy80dV9au6wf5OHXjcU1Ls6S1bh5xqSRlKRreL6V6uLKuGRetwIDAQAB"""
    )

    # 信付通 充值
    EpayTong_PAY_DEPOSIT = dict(
        provider="信付通",
        mch_id="100000000007984",
        # notifyUrl
        callback_url="https://{}/api/callback/v1/callback/epaytong/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        # returnUrl 支付成功跳转url
        return_url="https://127.0.0.1",
        post_url="https://ebank.xfuoo.com",
        deposit_path='/payment/v1/order/{}-{}',
        request_cls="app.channel.epaytong.deposit.request.DepositRequest",
        secret_key=os.getenv(
            'SECRET_KEY_Xft') or "amg6ipf5nhp74bkeqe1nl2k7logjba34o7cc22agxmsl6l9tczy3f54auja3wq27",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '154.218.7.68'],
    )
    # EpayTong_Pay_WITHDRAW
    EPAYTONG_PAY_WITHDRAW = dict(
        provider="信付通",
        mch_id="100000000007984",
        # notifyUrl
        callback_url="https://{}/api/callback/v1/callback/epaytong/withdraw".format(
            MerchantDomainConfig.get_callback_domain()),
        # returnUrl 支付成功跳转url
        return_url="https://192.168.0.1/#/login",
        post_url="https://client.xfuoo.com",
        withdraw_path='/agentPay/v1/batch/{}-{}',
        withdraw_cls="app.channel.epaytong.withdraw.request.WithdrawRequest",
        secret_key=os.getenv(
            'SECRET_KEY_Xft') or "bx8gi6n4m397xouwsndqyz978kj1njmdcw9kty2rugz2bnz15n8rlygtgvr0xw7r",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '154.218.7.68'],
    )
    # EPAYTONG_LARGE_WITHDRAW
    EPAYTONG_LARGE_WITHDRAW = dict(
        provider="信付通大额代付",
        mch_id="100000000007984",
        # notifyUrl
        callback_url="https://{}/api/callback/v1/callback/epaytong/withdraw".format(
            MerchantDomainConfig.get_callback_domain()),
        # returnUrl 支付成功跳转url
        return_url="https://192.168.0.1/#/login",
        post_url="https://client.xfuoo.com",
        withdraw_path='/agentPay/v1/batch/{}-{}',
        withdraw_cls="app.channel.epaytong.withdraw.request.WithdrawRequest",
        secret_key=os.getenv(
            'SECRET_KEY_Xft') or "bx8gi6n4m397xouwsndqyz978kj1njmdcw9kty2rugz2bnz15n8rlygtgvr0xw7r",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '154.218.7.68'],
    )

    Vpay_DEPOSIT = dict(
        provider="Vpay",
        mch_id="40",
        callback_url="https://{}/api/callback/v1/callback/vpay/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        post_url="https://dummy.hotec.club:9000/payApi",
        deposit_path='/deposit',
        request_cls="app.channel.vpay.deposit.request.DepositRequest",
        secret_key=os.getenv(
            'SECRET_KEY_Xft') or "2d02fee0-8ff7-4e32-a2d2-f984c941c978",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '47.52.96.1', '47.240.34.255']
    )

    RUKOUMY_DEPOSIT = dict(
        provider="Rukoumy",
        mch_id="32",
        callback_url="https://{}/api/callback/v1/callback/rukoumy/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        post_url="http://api.taiysg.com/api_v1",
        deposit_path='/ThirdPay',
        return_url="https://192.168.0.1/#/login",
        request_cls="app.channel.rukoumy.deposit.request.DepositRequest",
        DesKey="eayJFyqg",
        secret_key=os.getenv(
            'SECRET_KEY_rky') or "49aaffd2a60a4584aebd6f5922610f64",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '47.111.76.243', '47.111.71.235'],
    )

    BESTPAY_DEPOSIT = dict(
        provider="快手付",
        mch_id="421f12a834244cd8b0d8c02db79e5fdb",
        callback_url="https://{}/api/callback/v1/callback/bestpay/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        post_bank_info_url="http://www.bestpayapi.com:55168/",
        return_url="https://192.168.0.1/#/login",
        request_cls="app.channel.bestpay.deposit.request.DepositRequest",
        secret_key=os.getenv(
            'SECRET_KEY_btp') or "j4xqfvn6xcw1epv2gqcte7u0y4z5ckkyn7h98turmo2j70ou6bvdzlrb9xsbwitc",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '23.100.95.102'],
    )

    TONGYI_PAY_DEPOSIT = dict(
        provider="统一付",
        mch_id="10000101",
        callback_url="https://{}/api/callback/v1/callback/tongyi/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        post_url="http://47.107.254.140:3020/pay/",
        deposit_path='/buildorder',
        request_cls="app.channel.tongyi_pay.deposit.request.DepositRequest",
        secret_key=os.getenv(
            'SECRET_KEY_typ') or "27rr2ng1PDVx5kd",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '47.107.254.140'],
    )

    GPAY_DEPOSIT = dict(
        provider="Gpay-银联",
        mch_id="C1000096",
        callback_url="https://{}/api/callback/v1/callback/gpay/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        post_url="https://gapi.llque.com/api/v2/mownecum",
        deposit_path='/pay_request',
        request_cls="app.channel.gpay.deposit.request.DepositRequest",
        secret_key=os.getenv(
            'SECRET_KEY_typ') or "6k2wcQmCpSOZo97tVaOe1i08zlRxlVz5",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '3.0.191.50'],
    )

    JINZUAN_DEPOSIT = dict(
        provider="金钻",
        mch_id="C1000096",
        callback_url="https://{}/api/callback/v1/callback/jinzuan/deposit".format(
            MerchantDomainConfig.get_callback_domain()),
        post_url="https://api.jzpay.vip/jzpay_exapi/v1/order",
        deposit_path='/createOrder',
        request_cls="app.channel.jinzuan.deposit.request.DepositRequest",
        secret_key=os.getenv(
            'SECRET_KEY_typ') or "6k2wcQmCpSOZo97tVaOe1i08zlRxlVz5",
        white_ip=[
            "103.119.131.16", '127.0.0.1', '3.0.191.50'],
    )
