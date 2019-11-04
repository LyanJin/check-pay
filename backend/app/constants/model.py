import os

from app.libs.datetime_kit import DateTimeKit
from config import EnvironEnum

# 生成5年60张表，5年之后再修改 MAX_MONTHS 来增加新表
TABLE_MAX_MONTHS = 12 * 5

# !!!!!!! 警告，不可修改这行代码 !!!!!!!!!
TABLE_BEGIN_TIME = DateTimeKit.to_date(year=2019, month=7, day=1)
# !!!!!!! 警告，不可修改这行代码 !!!!!!!!!

if os.environ.get('UNIT_TEST') and os.getenv('FLASK_ENV') == EnvironEnum.DEVELOPMENT.value:
    # 加快单元测试速度
    TABLE_MAX_MONTHS = 12 * 1
    _cur_date = DateTimeKit.get_cur_datetime() - DateTimeKit.time_delta(days=30)
    TABLE_BEGIN_TIME = DateTimeKit.to_date(year=_cur_date.year, month=_cur_date.month, day=_cur_date.day)

# 热表数据保留 HOT_DAYS 天，超过 HOT_DAYS 的数据定期删除
TABLE_HOT_DAYS = 3

# 按列的值取模，不够2位数补零对齐
SHARD_COLUMN_FORMAT = "%02d"
