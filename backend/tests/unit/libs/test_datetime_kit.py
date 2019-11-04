import datetime

from app.libs.datetime_kit import DateTimeKit
from tests import TestNoneAppBase


class StringToolsTest(TestNoneAppBase):

    def test_datetime_kit(self):
        t = DateTimeKit.gen_midnight_timestamp()
        self.print("gen_midnight_timestamp, t: %s" % t)
        self.assertIsInstance(t, int)

        d = DateTimeKit.timestamp_to_datetime(t)
        self.print("timestamp_to_datetime, d: %s" % d)
        self.assertIsInstance(d, datetime.datetime)

        t = DateTimeKit.datetime_to_timestamp(d)
        self.print("datetime_to_timestamp, t: %s" % t)
        self.assertIsInstance(t, int)

        s = DateTimeKit.datetime_to_str(d)
        self.print("datetime_to_str, s: %s" % s)
        self.assertIsInstance(s, str)

        d = DateTimeKit.str_to_datetime(s)
        self.print("str_to_datetime, d: %s" % d)
        self.assertIsInstance(d, datetime.datetime)

        d = DateTimeKit.get_cur_date()
        self.print("get_cur_date, d: %s" % d)
        self.assertIsInstance(d, datetime.date)

        t = DateTimeKit.datetime_to_timestamp(d)
        self.print("datetime_to_timestamp, t: %s" % t)
        self.assertIsInstance(t, int)

        s = DateTimeKit.datetime_to_str(d)
        self.print("datetime_to_str, s: %s" % s)
        self.assertIsInstance(s, str)

        cur_time = DateTimeKit.get_cur_datetime()
        rst = DateTimeKit.is_month_begin_time(cur_time)
        self.assertFalse(rst)

        someday = DateTimeKit.to_date(year=2019, month=1, day=1)
        rst = DateTimeKit.is_month_begin_time(someday)
        self.assertTrue(rst)

        someday = DateTimeKit.to_date(year=2019, month=2, day=2)
        rst = DateTimeKit.is_month_begin_time(someday)
        self.assertFalse(rst)
