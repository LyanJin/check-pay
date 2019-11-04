import os
import traceback

import requests
from flask import current_app

from app.caches.epay_tong import EpayTongOrderCache
from app.channel.epaytong.deposit.callback import CallbackEpayTong
from app.channel.withdraw_base import ProxyPayRequest
from app.enums.channel import ChannelConfigEnum
from app.enums.trade import OrderStateEnum
from app.extensions import scheduler
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.logics.order.update_ctl import OrderUpdateCtl
from app.logics.transaction.withdraw_ctl import WithdrawTransactionCtl
from app.models.order.order_tasks import OrderTasks


class EpayTongWithdrawRequest(ProxyPayRequest):

    def gen_url(self, tx_id):
        mch_id = self.third_config['mch_id']
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['withdraw_path'].strip('/').format(mch_id, tx_id)
        return os.path.join(host, path)

    def construct_request(self, params_dict: dict):
        request_fields = ["batchDate", "batchNo", "batchVersion", "charset", "merchantId", "sign", "signType"]
        request_dict = dict()
        for field in request_fields:
            if field == "batchDate":
                request_dict[field] = params_dict["batch_date"]
            elif field == "batchNo":
                request_dict[field] = params_dict["tx_id"]
            elif field == "batchVersion":
                request_dict[field] = "00"
            elif field == "charset":
                request_dict[field] = "UTF-8"
            elif field == "merchantId":
                request_dict[field] = self.third_config['mch_id']

        sorted_fields = sorted(request_fields)
        sign_str = "&".join(
            ["{}={}".format(field, request_dict[field]) for field in sorted_fields if request_dict.get(field, False)])
        sign_str += self.third_config['secret_key']
        return request_dict, sign_str

    def parse_response(self, resp):
        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )
        data = resp.json()

        batchContent = data['batchContent']
        content = batchContent.split(',')
        tx_amount = content[8]
        tradeFeedbackcode = content[12]
        if data.get('respCode', False) == 'S0001':

            return dict(
                code=0,
                msg='ok',
                # 商户订单号
                data=dict(tx_id=data['batchNo'], tx_amount=tx_amount, tradeFeedbackcode=tradeFeedbackcode),
            )
        elif data.get('respCode', False) == "F9999":
            return dict(
                code=500,
                msg='通道系统异常',
                data=dict(tx_id=data['batchNo'])
            )
        elif data.get('respCode', False) == "F2001":
            return dict(
                code=404,
                msg='通道找不到该订单',
                data=dict(tx_id=data['batchNo'])
            )

        else:
            return dict(
                code=-999,
                msg='errorCode: {}, errorMsg:{}'.format(data.get('respCode', 'False'),
                                                        data.get('respMessage', 'False')),
                data=dict()
            )

    def launch_pay(self, params_dict):
        url = self.gen_url(params_dict['tx_id'])
        request_dict, sign_str = self.construct_request(params_dict)

        sign = CallbackEpayTong.gen_sign(sign_str)
        request_dict["sign"] = sign
        request_dict["signType"] = "SHA"

        try:
            current_app.logger.info('EpayTong withdraw check, url: %s, data: %s', url, request_dict)
            resp = requests.get(url=url, params=request_dict)
            current_app.logger.info('EpayTong withdraw check, order_id: %s, status_code: %s, content: %s',
                                     params_dict['tx_id'], resp.status_code,
                                     resp.text)
            print('EpayTong withdraw check, status_code: %s, content: %s', resp.status_code,
                  resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )
        return self.parse_response(resp)


@scheduler.task('interval', id='epay_tong_withdraw', minutes=3)
def withdraw_epay_tong():
    from app.main import flask_app
    with flask_app.app_context():

        tasks = list(OrderTasks.query_all())
        for task in tasks:
            order_id = task.order_id

            batch_date = DateTimeKit.datetime_to_str(task.create_time, DateTimeFormatEnum.TIGHT_DAY_FORMAT)

            current_app.logger.info('EpayTong withdraw check: order_id: %s, batch_date: %s', order_id, batch_date)
            order = WithdrawTransactionCtl.get_order_by_order_id(order_id)
            current_app.logger.info('EpayTong withdraw check: order_state: %s, state_type: %s', order.state,
                                     type(order.state))

            if not order:
                current_app.logger.info('EpayTong withdraw check, order_id: %s', order_id)
                OrderTasks.delete_task(task_id=task.id)
                continue

            if order.state.name == OrderStateEnum.SUCCESS.name or order.state.name == OrderStateEnum.FAIL.name:
                OrderTasks.delete_task(task_id=task.id)
                continue

            elif order.state.name != "DEALING":
                current_app.logger.info('EpayTong withdraw check, order_id: %s, order_state: %s', order_id,
                                         order.state)
                continue

            current_app.logger.info('EpayTong withdraw check, order_id: %s, order_state: %s', order_id,
                                     order.state)

            params = {
                "tx_id": order.sys_tx_id,
                "batch_date": batch_date
            }
            rst = EpayTongWithdrawRequest(channel_enum=ChannelConfigEnum.CHANNEL_6013).launch_pay(params)

            if rst['code'] == 0:
                tx_amount = rst['data']['tx_amount']
                code = rst['data']['tradeFeedbackcode']
                print(code, "******************")
                if code == "成功":
                    if WithdrawTransactionCtl.order_success(order, tx_amount):
                        OrderTasks.delete_task(task_id=task.id)

                elif code == "失败":
                    if WithdrawTransactionCtl.order_fail(order):
                        OrderTasks.delete_task(task_id=task.id)
