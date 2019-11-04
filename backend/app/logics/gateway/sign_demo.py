"""
python代码签名示例
"""
import hashlib


class SignDemo:

    @classmethod
    def generate_sign(cls, secret_key, params):
        keys = sorted(list(params.keys()))
        raw_str = '&'.join(["=".join(map(str, [k, params[k]])) for k in keys])
        raw_str += '&secret_key=' + secret_key
        print("raw_str:", raw_str)
        return hashlib.md5(raw_str.encode('utf8')).hexdigest()

    @classmethod
    def get_params(cls):
        return dict(
            zzzz=341432141243,
            xxxx='234113412',
            yyyy='你好啊啊啊',
            ffff=34143.2141243,
        )

    @classmethod
    def get_secret_key(self):
        return 'jBeyka%JbTuP_t#A1rx3SqpL*7XiIfNQ-oms&C925OUG)K+h(=w8^cFldEZ4RMW!'

    @classmethod
    def test(cls):
        secret_key = cls.get_secret_key()
        params = cls.get_params()
        sign = cls.generate_sign(secret_key, params)
        print('sign:', sign)
        return sign


if __name__ == '__main__':
    SignDemo.test()
    # print输出：
    """
    raw_str: ffff=34143.2141243&xxxx=234113412&yyyy=你好啊啊啊&zzzz=341432141243&secret_key=jBeyka%JbTuP_t#A1rx3SqpL*7XiIfNQ-oms&C925OUG)K+h(=w8^cFldEZ4RMW!
    sign: 00772fca2e8979c819f7a91cb73f5a03
    """
