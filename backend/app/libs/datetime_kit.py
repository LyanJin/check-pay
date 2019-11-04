"""时间和日期工具包
"""
import datetime
import functools
import time
from enum import Enum


class DateTimeFormatEnum(Enum):
    MONTH_FORMAT = "%Y-%m"
    TIGHT_MONTH_FORMAT = "%Y%m"

    DAY_FORMAT = "%Y-%m-%d"
    TIGHT_DAY_FORMAT = "%Y%m%d"

    MINUTES_FORMAT = "%Y-%m-%d %H:%M"
    TIGHT_MINUTES_FORMAT = "%Y%m%dT%H%M"

    SECONDS_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIGHT_SECONDS_FORMAT = "%Y%m%dT%H%M%S"

    HOURS_MINUTES_FORMAT = "%H:%M"
    TIGHT_HOURS_MINUTES_FORMAT = "%H%M"


class DateTimeKit:

    @classmethod
    def time_delta(cls, **kwargs):
        """
        时间差值对象
        :param kwargs: days, minutes, hours, seconds
        :return:
        """
        return datetime.timedelta(**kwargs)

    @classmethod
    def gen_midnight_timestamp(cls, days=1):
        """
        计算当前时间到将来几天后的午夜时间的秒数
        :param days:
        :return:
        """
        date = datetime.date.today() + cls.time_delta(days=days)
        return cls.datetime_to_timestamp(date)

    @classmethod
    def datetime_to_timestamp(cls, _datetime):
        """
        日期转换为时间戳
        :param _datetime:
        :return:
        """
        if isinstance(_datetime, datetime.datetime):
            # datetime继承自date，要先判断datetime
            pass
        elif isinstance(_datetime, datetime.date):
            date = _datetime
            _datetime = datetime.datetime(year=date.year, month=date.month, day=date.day)
        else:
            raise Exception('invalid datetime, type: %s' % type(_datetime))
        return int(_datetime.timestamp())

    @classmethod
    def timestamp_to_datetime(cls, timestamp, to_date=False):
        """
        日期转换为时间戳
        :param timestamp:
        :param to_date:
        :return:
        """
        sometime = datetime.datetime.fromtimestamp(timestamp)
        if to_date:
            return cls.to_date(sometime)
        return sometime

    @classmethod
    def str_to_datetime(cls, str_datetime, fmt: DateTimeFormatEnum = None, to_date=False):
        """
        字符串时间转datetime对象
        :param str_datetime:
        :param fmt:
        :param to_date:
        :return:
        """
        if not fmt:
            fmt = DateTimeFormatEnum.SECONDS_FORMAT

        d = datetime.datetime.strptime(str_datetime, fmt.value)
        return cls.to_date(d) if to_date else d

    @classmethod
    def datetime_to_str(cls, _datetime, fmt: DateTimeFormatEnum = None):
        """
        字符串时间转datetime对象
        :param _datetime:
        :param fmt:
        :return:
        """
        if not fmt:
            fmt = DateTimeFormatEnum.SECONDS_FORMAT
        return datetime.datetime.strftime(_datetime, fmt.value)

    @classmethod
    def get_cur_timestamp(cls, bit=1):
        """
        获取当前时间的时间戳
        :param bit: 精确小数多少位数, 比如3位bit=1000
        :return:
        """
        return int(time.time() * bit)

    @classmethod
    def get_cur_datetime(cls):
        """
        当前时间日期
        :return:
        """
        return cls.timestamp_to_datetime(cls.get_cur_timestamp())

    @classmethod
    def get_cur_date(cls):
        """
        当前日期
        :return:
        """
        return datetime.date.today()

    @classmethod
    def is_datetime(cls, value):
        return isinstance(value, (datetime.datetime, datetime.date))

    @classmethod
    def is_same_month(cls, date1, date2):
        return date1.year == date2.year and date1.month == date2.month

    @classmethod
    def to_datetime(cls, date=None, year=None, month=None, day=None, hour=None, minute=None):
        if date:
            return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=hour or 0, minute=minute or 0)
        else:
            return datetime.datetime(year=year, month=month, day=day, hour=hour or 0, minute=minute or 0)

    @classmethod
    def to_date(cls, date_time=None, year=None, month=None, day=None):
        if date_time:
            return datetime.date(year=date_time.year, month=date_time.month, day=date_time.day)
        else:
            return datetime.date(year=year, month=month, day=day)

    @classmethod
    def from_hour_minute(cls, hour, minute):
        """
        转换出成当天的某个时间对象
        :param hour:
        :param minute:
        :return:
        """
        cur_date = cls.get_cur_date()
        return cls.to_datetime(date=cur_date, hour=int(hour), minute=int(minute))

    @classmethod
    def change_digital_datetime_format(cls, digital_format):
        return datetime.datetime.strftime(datetime.datetime.strptime(digital_format, "%H:%M"), '%H:%M')

    @classmethod
    def get_day_begin_end(cls, someday, days=1, to_timestamp=False, to_date=False):
        """
        返回某天的开始/结束时间点，0:0:0 ~ 23:59:59
        :param someday:
        :param days:
        :param to_timestamp: 转换为timestamp
        :param to_date: 转换为date
        :return: 默认返回datetime
        """
        begin_time = cls.to_datetime(someday)
        # 先找第二天0点
        end_time = begin_time + cls.time_delta(days=days)
        # 转换为时间戳
        begin_ts, end_ts = cls.datetime_to_timestamp(begin_time), cls.datetime_to_timestamp(end_time)
        # 再转换为昨天23:59:59
        end_ts -= 1

        if to_timestamp:
            return begin_ts, end_ts

        return cls.timestamp_to_datetime(begin_ts, to_date), cls.timestamp_to_datetime(end_ts, to_date)

    @classmethod
    def get_month_begin_end(cls, year, month, to_timestamp=False, to_date=False):
        """
        返回某月的开始/结束时间点，0:0:0 ~ 23:59:59
        :param year:
        :param month:
        :param to_timestamp: 转换为timestamp
        :param to_date: 转换为date
        :return: 默认返回datetime
        """
        begin_time = cls.to_datetime(year=year, month=month, day=1)

        end_time = begin_time + cls.time_delta(days=40)
        end_time = cls.to_datetime(year=end_time.year, month=end_time.month, day=1)

        # 转换为时间戳
        begin_ts, end_ts = cls.datetime_to_timestamp(begin_time), cls.datetime_to_timestamp(end_time)
        # 再转换为昨天23:59:59
        end_ts -= 1

        if to_timestamp:
            return begin_ts, end_ts

        return cls.timestamp_to_datetime(begin_ts, to_date), cls.timestamp_to_datetime(end_ts, to_date)

    @classmethod
    def gen_month_range(cls, begin, months=1, to_timestamp=False):
        """
        生成月份列表
        :param begin:
        :param months:
        :param to_timestamp:
        :return:
        """
        dates = list()

        date = cls.to_datetime(begin, day=1)

        for x in range(months):
            if to_timestamp:
                dates.append(cls.datetime_to_timestamp(date))
            else:
                dates.append(date)

            # 跨月
            date += cls.time_delta(days=40)
            # 1号
            date = cls.to_datetime(date, day=1)

        return dates

    @classmethod
    def gen_date_range(cls, begin, days=1, to_timestamp=False):
        """
        返回天的列表
        :param begin:
        :param days:
        :param to_timestamp:
        :return:
        """
        dates = list()

        date = cls.to_datetime(begin)

        for x in range(days):
            if to_timestamp:
                dates.append(cls.datetime_to_timestamp(date))
            else:
                dates.append(date)

            date += cls.time_delta(days=1)

        return dates

    @classmethod
    def gen_hour_range(cls, someday, hours=24, to_timestamp=False, offset=1):
        """
        生成小时列表
        :param someday:
        :param hours:
        :param to_timestamp:
        :param offset:
            offset=0, 生成hour序列：[0, 1, 2 ... 22, 23]
            offset=1, 生成hour序列：[1，2，3 ... 23，24(第二天0点)]
        :return:
        """
        dates = list()

        begin_date = cls.to_datetime(someday)

        for x in range(offset, hours + offset):
            date = begin_date + cls.time_delta(hours=x)

            if to_timestamp:
                dates.append(cls.datetime_to_timestamp(date))
            else:
                dates.append(date)

        return dates

    @classmethod
    def get_cur_day_week(cls):
        return datetime.datetime.now().weekday()

    @classmethod
    def is_weekday(cls):
        """
        判断是否是周末
        :return:
        """
        return cls.get_cur_datetime().isoweekday()

    @classmethod
    def is_month_begin_time(cls, someday):
        """
        判断是否是一个月的开始时间，1号的0时0分0秒
        :param someday:
        :return:
        """
        if someday.day != 1:
            return False

        if isinstance(someday, (datetime.datetime,)):
            return someday.hour == 0 and someday.minute == 0 and someday.second == 0

        return True
