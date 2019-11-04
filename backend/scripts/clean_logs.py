"""
清理日志
"""
import os

from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from config import BASEDIR

log_path = 'logs'
log_prefix = 'flask.log.'


class LogCleaner:

    @classmethod
    def check_and_clean(cls, keep_days=7):

        full_path = os.path.join(BASEDIR, log_path)

        delete_files = list()

        for name in os.listdir(full_path):
            # print(name)
            if log_prefix not in name:
                continue

            try:
                date_str = name.split('.')[-1]
                date = DateTimeKit.str_to_datetime(date_str, DateTimeFormatEnum.DAY_FORMAT)
            except:
                continue

            delta_days = (DateTimeKit.get_cur_datetime() - date).days
            # print(delta_days, keep_days)
            if delta_days < keep_days:
                print('keep file: ', name)
                continue

            delete_files.append(name)

        for name in delete_files:
            file = os.path.join(full_path, name)
            print('removed ', file)
            os.remove(file)


if __name__ == '__main__':
    LogCleaner.check_and_clean()
