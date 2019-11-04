import time

from app.enums.admin import AdminModuleEnum
from app.libs.datetime_kit import DateTimeKit
from app.models.backoffice.admin_log import AdminLog
from tests import TestBackofficeUnitBase


class TestAdminLog(TestBackofficeUnitBase):
    ENABLE_PRINT = False
    ENABLE_SQL_LOG = False

    def __test_admin_log(self):
        begin_time = DateTimeKit.get_cur_datetime()

        data = dict(
            account='lucy',
            ip='127.0.0.1',
            module=AdminModuleEnum.SYSTEM,
            data_before=dict(x=1, y=2, c="你好"),
            data_after=dict(x=3, y=4, c="哈哈"),
        )
        AdminLog.add_log(**data)
        # time.sleep(1)

        end_time = DateTimeKit.get_cur_datetime()

        logs = list(AdminLog.query_log(begin_time, end_time))
        log = logs[0]
        self.assertEqual(len(logs), 1)
        self.assertEqual(log.account, data['account'])
        self.assertEqual(log.ip, data['ip'])
        self.assertEqual(log.module, data['module'])
        self.assertEqual(log.data_before, data['data_before'])
        self.assertEqual(log.data_after, data['data_after'])

        data = dict(
            account='clark',
            ip='192.168.12.233',
            module=AdminModuleEnum.TRADE,
            data_before=dict(x=1, y=2, c="你好"),
            data_after=dict(x=3, y=4, c="哈哈"),
        )
        AdminLog.add_log(**data)
        # time.sleep(1)
        end_time = DateTimeKit.get_cur_datetime()

        logs = list(AdminLog.query_log(begin_time, end_time))
        log = logs[1]
        self.assertEqual(len(logs), 2)
        self.assertEqual(log.account, data['account'])
        self.assertEqual(log.ip, data['ip'])
        self.assertEqual(log.module, data['module'])
        self.assertEqual(log.data_before, data['data_before'])
        self.assertEqual(log.data_after, data['data_after'])

        # 以日期查询，当天0点到第二天0点
        logs = list(AdminLog.query_log(begin_time.date(), end_time.date() + DateTimeKit.time_delta(days=1)))
        log = logs[1]
        self.assertEqual(len(logs), 2)
        self.assertEqual(log.account, data['account'])
        self.assertEqual(log.ip, data['ip'])
        self.assertEqual(log.module, data['module'])
        self.assertEqual(log.data_before, data['data_before'])
        self.assertEqual(log.data_after, data['data_after'])

        logs = list(AdminLog.query_by_account(begin_time, end_time, account='clark'))
        log = logs[0]
        self.assertEqual(len(logs), 1)
        self.assertEqual(log.account, data['account'])
        self.assertEqual(log.ip, data['ip'])
        self.assertEqual(log.module, data['module'])
        self.assertEqual(log.data_before, data['data_before'])
        self.assertEqual(log.data_after, data['data_after'])

        logs = list(AdminLog.query_all())
        self.assertEqual(len(logs), 2)
        AdminLog.delete_all()
        logs = list(AdminLog.query_all())
        self.assertEqual(len(logs), 0)

