import gevent.monkey

# gevent猴子补丁，在导入任何其它库之前调用
gevent.monkey.patch_all()

import os

# 部署环境
FLASK_ENV = os.getenv('FLASK_ENV') or 'development'
FLASK_SERVICE = os.getenv('FLASK_SERVICE')
print('FLASK_ENV: %s, FLASK_SERVICE: %s' % (FLASK_ENV, FLASK_SERVICE))

# 进程名称
proc_name = FLASK_SERVICE

# 主机:端口绑定
bind = "{}:{}".format(os.getenv("FLASK_HOST") or "127.0.0.1", (os.getenv('FLASK_PORT') or 8000))
print('bind: %s' % bind)

# 进程ID描述符存放路径
pidfile = "/tmp/gunicorn.pid"

# 以守护进程启动,docker里面不能使用守护进程后台运行，否则会直接退出，无法启动
# daemon = True

# The maximum number of pending connections.
backlog = 2048
# 使用gevent作为进行的工作模式
worker_class = 'gevent'
# The maximum number of simultaneous clients
# 设置为pool_size=100相等的大小，每个新的携程都会产生一个新的数据库链接
worker_connections = 100

# The maximum number of requests a worker will process before restarting.
# http://docs.gunicorn.org/en/latest/settings.html#max-requests
max_requests = 1000

# 在worker启动前预先加载代码
preload_app = True

# 启动的进程数，正式环境与cpu核心数对应起来
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1

# log级别
loglevel = 'error'

# log文件
# accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"

if FLASK_ENV in ['development', 'testing', ]:
    # 调试模式可以看到log
    debug = True
    # 测试环境启动2个就好了
    workers = 2
    # log级别
    # loglevel = 'debug'

if FLASK_ENV in ['development', ]:
    # 代码变更后自动重启
    reload = True

if FLASK_SERVICE in ['configuration', 'scheduler']:
    # 配置中心只需要启动一个进程
    workers = 1
