import os

import boto3


class SMSToolKit:

    AWS_SMS_REGION_NAME = os.getenv('AWS_SMS_REGION_NAME')
    AWS_SMS_KEY_ID = os.getenv('AWS_SMS_KEY_ID')
    AWS_SMS_KEY_VALUE = os.getenv('AWS_SMS_KEY_VALUE')

    def __init__(self, region_name=None, aws_access_key_id=None, aws_secret_access_key=None):
        self.client = boto3.client(
            'sns',
            # 默认使用"新加坡"地区的短信
            region_name=region_name or self.AWS_SMS_REGION_NAME or "ap-southeast-1",
            aws_access_key_id=aws_access_key_id or self.AWS_SMS_KEY_ID,
            aws_secret_access_key=aws_secret_access_key or self.AWS_SMS_KEY_VALUE,
        )

    def send_sms(self, phone_number, message):
        """
        通过AWS发送短信
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
        :param phone_number:
        :param message:
        :return:
        """
        response = self.client.publish(
            PhoneNumber=phone_number,
            Message=message,
        )
        # print(response)

        # When a messageId is returned, the message has been saved and Amazon SNS will attempt to deliver it shortly
        return 'MessageId' in response


if __name__ == '__main__':
    """
    测试需要先设置环境变量
    """
    # SMSToolKit().send_sms("+6391666602", "你好，Epay提醒，验证码是：8888，5分钟内有效")
    # SMSToolKit().send_sms("+86189755320", "你好，Epay提醒，验证码是：8888，5分钟内有效")
    SMSToolKit().send_sms("+86189755320", "hello, the code is 8888.")
