"""
https://zhuanlan.zhihu.com/p/46948464

"""
import traceback
from datetime import datetime
import os

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler


def tick():
    print('Tick! The time is: %s' % datetime.now())
    raise Exception('xxxx')


def my_listener(event):
    if event.exception:
        # print(traceback.format_exc())
        print('error occur')
    else:
        print("job running")


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=3)
    # scheduler.add_job(tick, 'cron', hour=19, minute=23)
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C    '))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('end')
