from urllib.parse import quote
import binascii
import hashlib
import hmac


class Sig(object):

    _sig = ''
    _secret_key = ''

    def __init__(self, secret_key):
        self._secret_key = secret_key

    @staticmethod
    def make_source(method, url_path, params):
        str_params = quote(
            '&'.join(k + '=' + str(params[k] or '') for k in sorted(params.keys())),
            '')
        source = '%s&%s&%s' % (method.upper(), quote(url_path, ''), str_params)
        return source

    def create(self, method, url_path, params):
        params.pop('sig', None)
        params.pop('data', None)
        params.pop('filter', None)

        source = self.make_source(method, url_path, params)
        hashed = hmac.new(self._secret_key.encode(),
                          source.encode(), hashlib.sha1)
        return quote(binascii.b2a_base64(hashed.digest())[:-1].decode(), '')

    def verifySign(self, method, url_path, params, sig):
        return self.create(method, url_path, params) == sig
