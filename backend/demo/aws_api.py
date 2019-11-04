import boto3


class SNSDemo:

    @property
    def client(self):
        return boto3.client(
            'sns',
            region_name="ap-southeast-1", # 新加坡
            aws_access_key_id="",
            aws_secret_access_key="",
        )

    def send_sms(self, phone_number, message):
        response = self.client.publish(
            PhoneNumber=phone_number,
            Message=message,
        )
        print(response)


if __name__ == '__main__':
    # SNSDemo().send_sms("+6391666602", "Hello, the code is 8888")
    SNSDemo().send_sms("+861897", "Hello, the code is 8888")
