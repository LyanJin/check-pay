import json

import requests

# https://blog.51cto.com/183530300/2124750

TOKEN = "925265552:AAFjArE5ptRx9t7zp34YBiLq77_-4p7l0fc"


def send_message(method, params=None):
    url = "https://api.telegram.org/bot{token}/{method}".format(token=TOKEN, method=method)
    print(url, params)
    rst = requests.get(url, params=params)
    print(json.dumps(rst.json(), indent=4))


if __name__ == '__main__':
    # send_message('getUpdates')

    # 服务器告警群
    send_message('sendMessage', params=dict(
        # chat_id="-350709901",
        chat_id="-348154837",
        text="testing bot"
    ))
