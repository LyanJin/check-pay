import json

from flask import request, current_app, url_for

from app.caches.deposit_render import DepositPageRenderCache
from app.enums.channel import ChannelConfigEnum
from app.enums.third_enum import SdkRenderType
from app.enums.trade import PayTypeEnum, OrderSourceEnum, InterfaceTypeEnum
from app.libs.datetime_kit import DateTimeKit
from app.libs.qr_code_kit import QRCodeKit
from app.libs.template_kit import TemplateKit
from app.libs.url_kit import UrlKit
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.models.merchant import MerchantFeeConfig


class DepositHelper:

    @classmethod
    def do_deposit_request(
            cls,
            user,
            channel_enum,
            amount,
            source: OrderSourceEnum,
            in_type: InterfaceTypeEnum,
            client_ip,
            user_agent,
            notify_url=None,
            mch_tx_id=None,
            result_url=None,
            extra=None,
    ):
        """
        创建充值订单，发起充值请求
        :return:
        """
        rst = dict(
            order=None,
            data=None,
            error=None
        )

        # 创建订单
        order, error = DepositTransactionCtl.order_create(
            user=user,
            amount=amount,
            channel_enum=channel_enum,
            client_ip=client_ip,
            source=source,
            in_type=in_type,
            notify_url=notify_url,
            result_url=result_url,
            mch_tx_id=mch_tx_id,
            extra=extra,
        )
        if error:
            rst['error'] = error.message
            return rst

        # 发起第三方支付请求
        launch_pay = channel_enum.get_launch_pay_func(PayTypeEnum.DEPOSIT)
        launch_rst = launch_pay(order, params=dict(
            channel_enum=channel_enum,
            client_ip=client_ip,
            user_agent=user_agent,
            # 如果通道需要，可以在用户支付完成后，重定向至这个页面
            result_url=result_url,
            user=user,
        ))

        if launch_rst['code'] != 0:
            current_app.logger.error(
                "do_deposit_request failed, merchant: %s, channel: %s, sys_tx_id: %s, client_ip: %s, launch_rst: %s",
                order.merchant.name, channel_enum.desc, order.sys_tx_id, client_ip, launch_rst)

            # 发起失败，直接把订单状态改成失败
            DepositTransactionCtl.order_create_fail(order)

            # 把第三方的错误信息提示出来
            rst['error'] = launch_rst['msg']
            return rst

        # 如果返回了通道订单号，那么更新订单保存起来
        channel_tx_id = launch_rst['data'].get('channel_tx_id')
        if channel_tx_id:
            DepositTransactionCtl.order_update(order, channel_tx_id)

        rst['order'] = order
        rst['data'] = launch_rst['data']

        # 解析跳转URL
        return rst

    @classmethod
    def parse_result(cls, data, order_id, endpoint, channel_enum):
        """
        解析第三方返回结果
        :param data:
        :param order_id:
        :param endpoint:
        :param channel_enum:
        :return:
        """
        rst = dict(
            redirect_url=None,
            # 默认是缓存过期时间
            valid_time=DepositPageRenderCache.EXPIRATION,
        )

        if data['render_type'] == SdkRenderType.URL:
            # 第三方提供了跳转页面，直接给url给客户端跳转
            rst['redirect_url'] = data['render_content']
        elif data['render_type'] == SdkRenderType.TRANSFER:
            DepositPageRenderCache(order_id).set_content(
                render_type=data['render_type'],
                render_content=data['render_content'],
                channel_enum=channel_enum.value,
                ttl=15 * 60
            )
            print('cache ttl:', DepositPageRenderCache(order_id).get_ttl())
            # 跳转到我们自己生成的页面
            rst['redirect_url'] = UrlKit.join_host_path(url_for(endpoint) + '?order_id=' + str(order_id))
        else:
            # 需要我方自行生成跳转页面，先把生成叶脉你需要的参数缓存起来
            DepositPageRenderCache(order_id).set_content(
                render_type=data['render_type'],
                render_content=data['render_content'],
                channel_enum=channel_enum.value,
            )

            print('cache ttl:', DepositPageRenderCache(order_id).get_ttl())

            # 跳转到我们自己生成的页面
            rst['redirect_url'] = UrlKit.join_host_path(url_for(endpoint) + '?order_id=' + str(order_id))

        return rst

    @classmethod
    def render_page(cls):
        """
        渲染页面
        :return:
        """
        print(request.args)

        try:
            order_id = request.args['order_id']
        except:
            return TemplateKit.render_template('deposit_simple.html', body="参数错误")

        order = DepositTransactionCtl.get_order_by_order_id(order_id)
        if not order:
            return TemplateKit.render_template('deposit_simple.html', body="订单不存在")

        cache = DepositPageRenderCache(order.order_id)
        cache_data = cache.get_content()
        print("&&&&&&&&&&&&&&", cache_data)
        if not cache_data:
            return TemplateKit.render_template('deposit_simple.html', body="订单已经过期")

        is_h5 = False
        prompt_msgs = []
        channel_enum = cache_data.get('channel_enum')
        if channel_enum:
            channel_enum = ChannelConfigEnum(int(channel_enum))
            prompt_msgs = channel_enum.get_prompt_info_detail()
            is_h5 = channel_enum.conf.payment_method.is_h5

        if cache_data['render_type'] == SdkRenderType.QR_CODE:
            merchant_config = MerchantFeeConfig.query_by_config_id(order.mch_fee_id)
            b64_img = QRCodeKit.gen_base64_qr_code_png(cache_data['render_content'])
            return TemplateKit.render_template(
                'deposit_qrcode.html',
                b64_img=b64_img,
                payment_type=merchant_config.payment_method.desc,
                sys_tx_id=order.sys_tx_id,
                amount=str(order.amount),
                valid_time=cache.EXPIRATION,
                payment_url=cache_data['render_content'] if is_h5 else None,
                prompt_msgs=prompt_msgs,
            )

        if cache_data['render_type'] == SdkRenderType.FORM:
            return TemplateKit.render_template('deposit_base.html', body=cache_data['render_content'])

        if cache_data['render_type'] == SdkRenderType.HTML:
            return TemplateKit.render_template_string(cache_data['render_content'])

        if cache_data['render_type'] == SdkRenderType.TRANSFER:
            data = json.loads(cache_data['render_content'], encoding='utf8')
            return TemplateKit.render_template(
                'bank.html',
                CardName=data['CardName'],
                CardNumber=data['CardNumber'],
                BankName=data['BankName'],
                amount=data['amount'],
                tx_id=data['tx_id'],
                start_time=data['start_time']
            )

        current_app.logger.error('failed to render page, order_id: %s, cache_data: %s', order.order_id, cache_data)

        return TemplateKit.render_template('deposit_simple.html', body="渲染失败")
