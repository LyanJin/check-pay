def check_sign():
    from app.main import flask_app
    from app.channel.ponypay.withdraw.callback import WithdrawCallbackPonypay
    from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
    from app.models.channel import ChannelConfig

    tx_id = "TEST|5D4986A0|C|7"
    tx_amount = "100.00"
    sign = "AB06CBBA87CB9D5C94DF9564DBAA6C52"

    with flask_app.app_context():
        order = WithdrawTransactionCtl.get_order(tx_id)
        channel_config = ChannelConfig.query_by_channel_id(order.channel_id)
        controller = WithdrawCallbackPonypay(channel_config.channel_enum)
        print(controller.generate_sign(tx_id, tx_amount))
        print(controller.check_sign(tx_id, tx_amount, sign))


if __name__ == '__main__':
    check_sign()
