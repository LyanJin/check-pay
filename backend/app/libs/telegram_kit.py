import json

import requests

# https://blog.51cto.com/183530300/2124750

TOKEN = "925265552:AAFjArE5ptRx9t7zp34YBiLq77_-4p7l0fc"
TG_GROUP_DEV = "-350709901"
TG_GROUP_OPT = "-348154837"


class TelegramKit:

    @classmethod
    def send_message(cls, method, params=None):
        url = "https://api.telegram.org/bot{token}/{method}".format(token=TOKEN, method=method)
        # print(url, params)
        rst = requests.get(url, params=params)
        # print(json.dumps(rst.json(), indent=4))

    @classmethod
    def send_server_alert_message(cls, msg):
        # 开发群告警
        cls.send_message('sendMessage', params=dict(
            chat_id=TG_GROUP_DEV,
            text=msg
        ))

    @classmethod
    def send_operation_alert_message(cls, msg):
        # 运营群告警
        cls.send_message('sendMessage', params=dict(
            chat_id=TG_GROUP_OPT,
            text=msg
        ))
