"""
存款渲染页面
"""
from app.caches.base import RedisHashCache
from app.caches.keys import PAGE_RENDER_CACHE_KEY_PREFIX
from app.constants.trade import DEPOSIT_ORDER_TTL
from app.enums.third_enum import SdkRenderType


class DepositPageRenderCache(RedisHashCache):
    EXPIRATION = DEPOSIT_ORDER_TTL
    KEY_PREFIX = PAGE_RENDER_CACHE_KEY_PREFIX

    def __init__(self, order_id):
        super(DepositPageRenderCache, self).__init__(suffix=order_id)

    def set_content(self, render_type: SdkRenderType, render_content, channel_enum, ttl=None):
        data = dict(
            render_type=str(render_type.name),
            render_content=render_content,
            channel_enum=channel_enum,
        )
        rst = self.hmset(data)
        self.update_expiration(ttl=ttl)
        return rst

    def get_content(self):
        data = self.hgetall()
        if not data:
            return None

        return dict(
            render_type=SdkRenderType.from_name(data[b'render_type'].decode('utf8')),
            render_content=data[b'render_content'].decode('utf8'),
            channel_enum=data[b'channel_enum'].decode('utf8'),
        )


if __name__ == "__main__":
    from app.main import flask_app

    with flask_app.app_context():
        cache = DepositPageRenderCache(111)
        rd_type = SdkRenderType.URL
        ctn = 'https:/google.com?x=1y=2'
        cache.set_content(rd_type, ctn)
        ret = cache.get_content()
        assert ret['render_type'] == rd_type
        assert ret['render_content'] == ctn
        assert cache.get_ttl() <= cache.EXPIRATION

        cache = DepositPageRenderCache(2341414)
        rd_type = SdkRenderType.FORM
        ctn = '<!DOCTYPE html></body></html>'
        cache.set_content(rd_type, ctn)
        ret = cache.get_content()
        assert ret['render_type'] == rd_type
        assert ret['render_content'] == ctn
        assert cache.get_ttl() <= cache.EXPIRATION
