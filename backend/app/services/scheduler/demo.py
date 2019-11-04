from app.extensions import scheduler


# @scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
def job1():
    # interval examples
    print('Job 1 executed')


# @scheduler.task('cron', id='do_job_2', minute='*')
def job2():
    # cron examples
    print('Job 2 executed')