# 后端代码
this is the backend project to merchant.

## Getting start

1. 注册gitlab账号

	https://gitlab.com/users/sign_in#register-pane

2. 安装python3.7

	https://www.python.org/downloads/release/python-370/

3. 安装pycharm 专业版：

	https://blog.csdn.net/u010299280/article/details/89467940

4. 安装pipenv，在pycharm中配置好 pipenv环境。

	https://zhuanlan.zhihu.com/p/33407501
	or 
	https://www.jetbrains.com/help/pycharm/pipenv.html

5. 用pipenv安装python以来包，

	cd epay/backend/
	pipenv sync

6. 配置环境变量为cashier

	epay/bakcend/config.py
	FLASK_SERVICE = os.getenv('FLASK_SERVICE') or ServiceEnum.CASHIER.value

7. 配置测试商户域名，把本机IP地址配置到test商户下：

	class MerchantDomainConfig:
	    __domains = {
	        MerchantEnum.TEST: [
	            '127.0.0.1',
	            'localhost',
	            '192.168.1.10',
	        ],
	        MerchantEnum.QF2: [
	        ],
	        MerchantEnum.QF3: [
	        ],
	    }

8. 同步数据库

	python manage.py db upgrade

9. 启动服务

	cd epay/bakcend/
	python run_debug.py

10. 浏览器打开API文档，可以对API进行调试了

	http://127.0.0.1:7082/doc/cashier/v1




## 项目模块简介

    from werkzeug.utils import find_modules, import_string
    for name in find_modules('app', include_packages=True, recursive=False):
        mod = import_string(name)
        print("##### 模块：%s\n概述：%s" % (mod.__name__, mod.__doc__))


##### 模块：app.caches
概述：缓存模块

##### 模块：app.constants
概述："常量定义

##### 模块：app.docs
概述：文档模型描述，用来定义期望客户端传入的表单模型，或者返回给客户端的数据模型，自动生成文档

##### 模块：app.enums
概述：枚举定义

##### 模块：app.extensions
概述：Flask扩展对象初始化

##### 模块：app.forms
概述：表单验证模块

##### 模块：app.libs
概述：公共的类库，这里不写业务逻辑

##### 模块：app.logics
概述：业务逻辑代码实现放这个模块,提供给service调用

##### 模块：app.models
概述：数据模型定义

##### 模块：app.services
概述：服务注册和初始化，每个服务一个目录，在发布时用环境变量分开来部署



## 数据库同步命令：

根据module生成sql脚本

    python manage.py db init --multidb

根据module生成sql脚本

    python manage.py db migrate -m "备注信息"

执行sql脚本到数据库

    python manage.py db upgrade

撤销执行sql脚本

    python manage.py db downgrade
