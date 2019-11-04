import os
import traceback
from decimal import Decimal

import requests
from flask import current_app

from app.caches.epay_tong import EpayTongOrderCache
from app.channel.epaytong.withdraw.callback import CallbackEpayTong
from app.channel.withdraw_base import ProxyPayRequest
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.models.order.order_tasks import OrderTasks

EPayTongBank = dict(
    CMB="招商银行",
    BOC="中国银行",
    ICBC="中国工商银行",
    CCB="中国建设银行",
    ABC="中国农业银行",
    PSBC="中国邮政储蓄银行",
    SPDB="上海浦东发展银行",
    CMBC="中国民生银行",
    SPABANK="平安银行",
    HXBANK="华夏银行",
    CITIC="中信银行",
    CEB="中国光大银行",
    CIB="兴业银行",
    GDB="广发银行",
    COMM="交通银行"
)


class WithdrawRequest(ProxyPayRequest):

    def parse_response(self, resp, params_dict: dict):

        if resp.status_code != 200:
            return dict(
                code=-100,
                msg='http请求失败，状态: %s' % resp.status_code,
                data=dict(),
            )

        data = resp.json()

        tx_id = params_dict['tx_id']
        if data.get("respCode", "") == "S0001":
            OrderTasks.insert_task(params_dict['order_id'])
            return dict(
                code=0,
                msg='ok',
                # 商户订单号
                data=dict(tx_id=params_dict['tx_id']),
            )
        else:
            return dict(
                code=-999,
                msg='errorCode: {}, errorMsg:{}'.format(data.get('respCode', 'False'),
                                                        data.get('respMessage', 'False')),
                data=dict()
            )

    def gen_url(self, tx_id):
        mch_id = self.third_config['mch_id']
        host = self.third_config['post_url'].strip('/')
        path = self.third_config['withdraw_path'].strip('/').format(mch_id, tx_id)
        return os.path.join(host, path)

    def construct_request(self, params_dict: dict):

        tx_id = params_dict['tx_id']

        request_fields = ["batchAmount", "batchBiztype", "batchContent", "batchCount", "batchDate", "batchNo",
                          "batchVersion", "charset", "merchantId", "sign", "signType"]
        request_dict = dict()
        for field in request_fields:
            if field == "batchAmount":
                request_dict[field] = Decimal(params_dict['amount'])
            elif field == "batchBiztype":
                request_dict[field] = "00000"
            elif field == "batchContent":
                branch = params_dict['bank_branch']
                if not branch:
                    branch = "分行"

                branch_ = params_dict['bank_branch']
                if not branch_:
                    branch_ = "支行"
                # {序号},{银行账户},{开户名},{开户行名称},{分行},{支行},{公/私},{金额},{币种},{省},{市},{手机号},{证件类型},{证件号},{用户协议号},{商户订单号},{备注}
                request_dict[
                    field] = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                    1, params_dict['bank_number'], params_dict['bank_account'], EPayTongBank[params_dict['bank_code']],
                    branch, branch_,
                    0, Decimal(params_dict['amount']), "CNY", params_dict["province"], params_dict["city"], "", "", "",
                    "", tx_id, "withdraw amount")
            elif field == "batchCount":
                request_dict[field] = "1"
            elif field == "batchDate":
                request_dict[field] = params_dict['batch_date']
            elif field == "batchNo":
                request_dict[field] = params_dict['tx_id']
            elif field == "batchVersion":
                request_dict[field] = "00"
            elif field == "charset":
                request_dict[field] = "UTF-8"
            elif field == "merchantId":
                request_dict[field] = self.third_config['mch_id']

        sorted_params = sorted(request_fields)
        sign_str = "&".join(["{}={}".format(k, request_dict[k]) for k in sorted_params if request_dict.get(k, False)])

        sign_str += self.third_config['secret_key']

        print("sign string: ", sign_str)
        print("request body: ", request_dict)

        return request_dict, sign_str

    def launch_pay(self, params_dict: dict):
        """
        发起代付
        :param params_dict:
        :return:
        """

        url = self.gen_url(params_dict['tx_id'])

        params_dict['batch_date'] = DateTimeKit.datetime_to_str(DateTimeKit.get_cur_datetime(),
                                                                  DateTimeFormatEnum.TIGHT_DAY_FORMAT)
        request_dict, sign_str = self.construct_request(params_dict)

        sign = CallbackEpayTong.generate_sign(sign_str)

        request_dict["sign"] = sign
        request_dict["signType"] = "SHA"

        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            current_app.logger.info('EpayTong withdraw, url: %s, data: %s', url, request_dict)
            resp = requests.post(url=url, data=request_dict, headers=headers)
            current_app.logger.info('EpayTong withdraw, status_code: %s, content: %s', resp.status_code, resp.text)
        except Exception as e:
            current_app.logger.fatal(traceback.format_exc())
            return dict(
                code=-100,
                msg="http请求失败",
                data=dict(),
            )

        print(resp.json(), resp.text, resp.content)
        return self.parse_response(resp, params_dict)
