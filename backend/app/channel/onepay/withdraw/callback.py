from app.channel.withdraw_base import ProxyPayRequest
from app.enums.third_config import ThirdPayConfig
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import base64
import binascii


class CallbackOnePay:

    @staticmethod
    def gen_sign(body_str, third_config):
        signer = PKCS1_v1_5.new(RSA.importKey(third_config['plat_private_key']))
        body_str_byte = body_str.encode('utf8')
        hash_value = SHA.new(body_str_byte)
        sharsa = signer.sign(hash_value)
        return base64.b64encode(sharsa).hex()

    @staticmethod
    def check_sign(sign, plaintext, third_config):
        desc_sign = binascii.unhexlify(sign.encode('utf8'))
        hash_value = SHA.new(plaintext.encode('utf8'))
        verifier = PKCS1_v1_5.new(RSA.importKey(base64.b64decode(third_config['plat_public_key'])))
        return verifier.verify(hash_value, base64.b64decode(desc_sign))
