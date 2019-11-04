class DaemonJobs:
    def __init__(self, _app=None):
        self.app = _app

    def init_jobs(self, _app=None):
        """
        初始化在守护进程运行的任务
        :param _app:
        :return:
        """
        if _app:
            self.app = _app

        self.app.logger.info('begin to initial daemon jobs')

        # self.add_job_sync_merchant_cache()

        self.app.logger.info('done to initial daemon jobs')

    # def add_job_sync_merchant_cache(self):
    #     """
    #     同步商户配置信息到缓存
    #     :return:
    #     """
    #     from .cache_sync import job_sync_merchant_cache
    #
    #     kwargs = dict(hours=1)
    #     if self.app.config['DEBUG']:
    #         kwargs = dict(seconds=10)
    #     elif self.app.config['TESTING']:
    #         kwargs = dict(minutes=1)
    #
    #     self.app.apscheduler.add_job(
    #         id="job_sync_merchant_cache",
    #         func=job_sync_merchant_cache,
    #         trigger="interval",
    #         **kwargs,
    #     )
