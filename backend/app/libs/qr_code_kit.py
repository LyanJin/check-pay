import base64
import io

import qrcode


class QRCodeKit:

    @classmethod
    def gen_base64_qr_code_png(cls, url):
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        image_stream = buf.getvalue()
        base64_img = base64.b64encode(image_stream)
        base64_img = 'data:image/png;base64,' + base64_img.decode()
        return base64_img
