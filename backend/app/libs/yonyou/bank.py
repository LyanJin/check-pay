import os
import requests
import json


class BankToolKit:

    YY_API_CODE = os.getenv('YY_API_CODE')

    def __init__(self, apicode=None):
        self.apicode = apicode or self.YY_API_CODE or 'd74c59f4d3b14e91b02f3118b43d52ca'

    def get_bank_location(self, CardID):
        """
        根据银行卡卡号获取相关的信息
        https://api.yonyoucloud.com/apis/dst/banklocation/banklocation
        :param CardID:
        :return:
        """

        url = "https://api.yonyoucloud.com/apis/dst/banklocation/banklocation"

        querystring = {"CardID": CardID}

        headers = {'apicode': self.apicode}

        response = requests.get(url, headers=headers, params=querystring)

        print(response.text)

        try:
            return response.json()
        except:
            return dict()


if __name__ == '__main__':
    """
    测试需要先设置环境变量
    """
    BankToolKit().get_bank_location("6212260405014627955")
