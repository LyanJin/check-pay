import json
from decimal import Decimal

from werkzeug.wrappers import BaseResponse

from app.channel.bestpay.deposit.callback import CallbackBestPay
from app.enums.third_config import ThirdPayConfig
from app.libs.datetime_kit import DateTimeKit
from app.logics.transaction.deposit_ctl import DepositTransactionCtl
from app.models.order.order_tasks import OrderTransferLog
from . import api
from config import EnvironEnum
from flask import current_app, request
from app.libs.ip_kit import IpKit
from flask_restplus import Resource
from app.libs.doc_response import ResponseDoc
from app.enums.trade import OrderStateEnum

ns = api.namespace('callback', description='用户充值')


@ns.route('/bestpay/deposit')
@ResponseDoc.response(ns, api)
class BestPayDeposit(Resource):
    def post(self):
        """
        BestPay，充值回调
        :return:
        """
        if not EnvironEnum.is_local_evn(current_app.config['FLASK_ENV']):
            # 无论如何都记录一条log
            current_app.logger.info('BestPay deposit callback, ip: %s, data: %s', IpKit.get_remote_ip(), request.form)

        client_ip = IpKit.get_remote_ip()
        if not CallbackBestPay.check_ip(client_ip):
            current_app.logger.error('ip not allow, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     request.form)
            return BaseResponse('error')

        data = request.form['deposit_result']
        resp_body = json.loads(data)

        third_config = ThirdPayConfig.BESTPAY_DEPOSIT.value
        sign = resp_body["sign"]
        resp_type = resp_body["type"]
        if resp_type != "deposit_result":
            return BaseResponse('error')
        data = resp_body["data"]

        print(data)
        if isinstance(data, list):
            sign_str = json.dumps(data)
        else:
            sign_str = data
        sign_str += third_config['secret_key']
        flag = CallbackBestPay.check_sign(sign, sign_str)
        if not flag:
            current_app.logger.error('invalid sign, client_ip: %s, data: %s, body: %s', client_ip, request.args,
                                     sign_str)
            return BaseResponse('error')

        data_list = json.loads(data)
        flag = 'error'
        for data_dict in data_list:

            order_id = data_dict['client_postscript']
            tx_amount = data_dict['amount']
            channel_tx_id = data_dict['order_number']
            client_transtype = data_dict['client_transtype']
            deposit_cardnumber = data_dict['deposit_cardnumber']
            user_name = data_dict['client_accountname']
            deposit_time = data_dict['deposit_time']

            try:
                order_id = int(order_id)
            except Exception as e:
                if client_transtype == '微信转账':
                    DateTimeKit.time_delta()
                    log = OrderTransferLog.query_transfer_log_by_user_info(
                        deposit_cardnumber=deposit_cardnumber,
                        amount='{:.2f}'.format(float(tx_amount)),
                        deposit_time=deposit_time
                    )
                else:

                    log = OrderTransferLog.query_transfer_log_by_user_info(
                        deposit_cardnumber=deposit_cardnumber,
                        amount='{:.2f}'.format(float(tx_amount)),
                        client_accountname=user_name,
                        deposit_time=deposit_time
                    )
                current_app.logger.info("转账信息数据", log)
                if log:

                    for o in log:

                        order = DepositTransactionCtl.get_order_by_order_id(order_id=o.order_id)
                        if not order or order.state.name != OrderStateEnum.INIT.name:
                            continue

                        if DepositTransactionCtl.success_order_process(order, Decimal(str(tx_amount)), channel_tx_id):
                            OrderTransferLog.update_transfer_log(order_id=order.order_id)
                            flag = "success"

            else:

                log = OrderTransferLog.query_transfer_log(order_id=order_id)
                if not log:
                    continue

                order = DepositTransactionCtl.get_order_by_order_id(order_id=log.order_id)

                if not order or order.state.name != OrderStateEnum.INIT.name:
                    continue

                if DepositTransactionCtl.success_order_process(order, Decimal(str(tx_amount)), channel_tx_id):
                    OrderTransferLog.update_transfer_log(order_id=order.order_id)
                    flag = "success"

        return BaseResponse(flag)
