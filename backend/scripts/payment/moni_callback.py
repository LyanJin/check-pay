from app.enums.channel import ChannelConfigEnum


def callback_jifu():
    import requests
    from app.channel.jifu.deposit.callback import DepositCallbackJifu
    data = dict(
        nonce_str='123413212412',
        id='9c1678cc2775d034',
        money='200.00',
        remark='E56836049349578700000308',
    )
    sign = DepositCallbackJifu(ChannelConfigEnum.CHANNEL_7001).generate_sign(data)
    data['sign'] = sign
    rsp = requests.post("https://callback.epay1001.com/api/callback/v1/callback/jifu/deposit", data)
    print(rsp.status_code)
    print(rsp.text)


if __name__ == '__main__':
    # from scripts.payment.moni_callback import *
    callback_jifu()
