from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import Crypto.Hash.SHA512
import base64
import hmac
import hashlib


class CryptoKit:

    @classmethod
    def hmac_sign(cls, bytes_data, bytes_secret, bit=256):
        """hmac签名"""
        if bit == 256:
            digest = hashlib.sha256
        elif bit == 512:
            digest = hashlib.sha512
        else:
            return ''
        signature = hmac.new(
            bytes_secret,
            msg=bytes_data,
            digestmod=digest,
        ).hexdigest()
        return signature

    @classmethod
    def rsa_sign(cls, plaintext, key, bit=256):
        """RSA 数字签名"""
        if bit == 256:
            algorithm = Crypto.Hash.SHA256
        elif bit == 512:
            algorithm = Crypto.Hash.SHA512
        else:
            return ''
        # signer = PKCS1_v1_5.new(base64.b64decode(RSA.importKey(key)))
        signer = PKCS1_v1_5.new(RSA.importKey(key))
        # hash算法必须要pycrypto库里的hash算法，不能直接用系统hashlib库，pycrypto是封装的hashlib
        hash_value = algorithm.new(plaintext)
        return base64.b64encode(signer.sign(hash_value))

    @classmethod
    def rsa_verify(cls, sign, plaintext, key, bit=256):
        """校验RSA 数字签名"""
        if bit == 256:
            algorithm = Crypto.Hash.SHA256
        elif bit == 512:
            algorithm = Crypto.Hash.SHA512
        else:
            return ''
        hash_value = algorithm.new(plaintext.encode('utf8'))
        verifier = PKCS1_v1_5.new(RSA.importKey(base64.b64decode(key)))
        return verifier.verify(hash_value, base64.b64decode(sign))

