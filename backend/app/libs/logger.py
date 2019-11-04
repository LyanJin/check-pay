import codecs
import logging
import os
from logging.handlers import BaseRotatingHandler

from logstash import TCPLogstashHandler

from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum


class MyTCPLogstashHandler(TCPLogstashHandler):

    def __init__(self, host, port=5959, message_type='logstash', tags=None, fqdn=False, version=0, level=logging.INFO):
        super(MyTCPLogstashHandler, self).__init__(host, port, message_type, tags, fqdn, version)
        self.level = level

    def emit(self, record):
        try:
            from app.services.celery.async_log import async_send_log_to_socket
            if record.levelno >= self.level:
                s = self.makePickle(record)
                async_send_log_to_socket.delay(host=self.host, port=self.port, msg=s.decode('utf8'))
        except Exception:
            self.handleError(record)


class MultiProcessSafeDailyRotatingFileHandler(BaseRotatingHandler):
    """Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported

    https://my.oschina.net/lionets/blog/796438

    """
    def __init__(self, log_path, filename, keep_days=7, emit_tg=True, environment=""):
        self.emit_tg = emit_tg
        self.environment = environment
        self.suffix_format = DateTimeFormatEnum.DAY_FORMAT
        self.keep_days = keep_days
        self.log_path = log_path
        self.filename = filename
        self.base_file = os.path.join(log_path, filename)
        self.current_file = self.get_current_file()
        BaseRotatingHandler.__init__(self, self.base_file, 'a', 'utf-8', delay=False)

    def emit(self, record: logging.LogRecord):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.should_rollover(record):
                self.do_rollover()
            logging.FileHandler.emit(self, record)

            # 发送消息给TG
            if record.levelno >= logging.ERROR and self.emit_tg:
                msg = self.format(record)
                msg = "Environment: %s\n%s" % (self.environment, msg)
                from app.services.celery.async_log import async_send_log_to_telegram
                async_send_log_to_telegram.delay(msg=msg)
        except Exception:
            self.handleError(record)

    def should_rollover(self, record):
        c_file = self.get_current_file()
        if self.current_file != c_file:
            return True
        return False

    def do_rollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.current_file = self.get_current_file()
        self.check_and_clean()

    def get_suffix(self, cur_datetime=None):
        cur_datetime = cur_datetime or DateTimeKit.get_cur_datetime()
        return DateTimeKit.datetime_to_str(cur_datetime, self.suffix_format)

    def parse_suffix(self, filename):
        date_str = filename.split('.')[-1]
        return DateTimeKit.str_to_datetime(date_str, self.suffix_format)

    def get_current_file(self):
        return self.base_file + "." + self.get_suffix()

    def _open(self):
        if self.encoding is None:
            stream = open(self.current_file, self.mode)
        else:
            stream = codecs.open(self.current_file, self.mode, self.encoding)

        # simulate file name structure of `logging.TimedRotatingFileHandler`
        if os.path.exists(self.base_file):
            try:
                os.remove(self.base_file)
            except OSError:
                pass

        try:
            os.symlink(self.current_file, self.base_file)
        except OSError:
            pass

        return stream

    def check_and_clean(self):

        delete_files = list()

        for name in os.listdir(self.log_path):
            # print(name)
            if name == self.filename:
                continue

            try:
                date = self.parse_suffix(name)
            except:
                continue

            delta_days = (DateTimeKit.get_cur_datetime() - date).days
            # print(delta_days, keep_days)
            if delta_days < self.keep_days:
                print('keep file: ', name)
                continue

            delete_files.append(name)

        for name in delete_files:
            file = os.path.join(self.log_path, name)
            print('to remove', file)
            if os.path.exists(file):
                print('removed ', file)
                os.remove(file)
