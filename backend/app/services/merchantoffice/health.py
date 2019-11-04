from flask_restplus import Resource

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
