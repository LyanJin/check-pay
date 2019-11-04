from flask_restplus import Resource

from app.extensions import redis
from app.libs.error_code import ResponseSuccess
from app.models.order.order_tst import OrderDepositTst
from . import api

ns = api.namespace('health', description='接口联通性测试')

DEBUG_LOG = False


@ns.route('/check')
class ConnectionCheck(Resource):
    def get(self):
        """
        联通性测试
        :return:
        """
        return 'ok'


@ns.route('/load/balance/check')
class LoadBalanceCheck(Resource):
    def get(self):
        """
        检查负载均衡
        :return:
        """
        import socket
        host = socket.gethostname()
        times = redis.incr('slb_check')
        return ResponseSuccess(bs_data=dict(
            host=host,
            times=times,
        )).as_response()


@ns.route('/tst/order/create')
class TstCreateOrder(Resource):
    def get(self):
        """
        测试创建订单
        :return:
        """
        rst = OrderDepositTst.create_order()
        return ResponseSuccess(bs_data=dict(
            code=rst['code'],
            msg=rst['msg'],
        )).as_response()


@ns.route('/tst/order/query')
class TstQueryOrder(Resource):
    def get(self):
        """
        测试查询订单
        :return:
        """
        count = OrderDepositTst.count_all_records()
        return ResponseSuccess(bs_data=dict(
            count=count,
        )).as_response()


@ns.route('/tst/order/drop/all')
class TstDropOrder(Resource):
    def get(self):
        """
        测试查询订单
        :return:
        """
        OrderDepositTst.drop_all_records()
        count = OrderDepositTst.count_all_records()
        return ResponseSuccess(bs_data=dict(
            count=count,
        )).as_response()
