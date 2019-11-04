from app.enums.base_enum import BaseEnum


class SdkRenderType(BaseEnum):
    # 是一个url，前端直接打开这个url即可
    URL = 0
    # 需要前端生成二维码
    QR_CODE = 1
    # 返回表单内容给前端渲染
    FORM = 7
    # 返回整个页面
    HTML = 8
    # 转账页面
    TRANSFER = 9
