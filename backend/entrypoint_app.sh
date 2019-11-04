#!/usr/bin/env bash

echo "[$(date)] begin initialize flask service $FLASK_SERVICE"

# 创建logs目录
if [ ! -d "logs" ]; then
    echo "[$(date)] mkdir logs"
    mkdir logs
fi

# 创建sqlites目录,测试环境sqlite使用
if [ ! -d "sqlites" ]; then
    echo "[$(date)] mkdir sqlites"
    mkdir sqlites
fi


if [ "$FLASK_SERVICE" == 'configuration' ]; then
    # 初始化配置中心
    # 要等待db启动完毕后才能进行配置
    echo "[$(date)] DB_HOST: $DB_HOST"
    while ! nc -z $DB_HOST 3306; do
        echo "[$(date)] waiting for database";
        sleep 5;
    done;

    echo "[$(date)] database is ready!";

    # 同步数据库
    echo "[$(date)] python manage.py db upgrade"
    python manage.py db upgrade

    # 初始化数据
    echo "[$(date)] python manage.py init_db"
    python manage.py init_db

else
    # 等待配置中心加载配置完毕后再启动服务
    while ! nc -z configuration 20001; do
        echo "[$(date)] waiting for configuration";
        sleep 5;
    done;

    echo "[$(date)] configuration is ready!";
fi

# 执行CMD
# 如果docker run时没有指定CMD，那么会使用dockerfile中的CMD
# 如果docker run时指定了CMD，那么dockerfile中的CMD会被忽律
echo "$@"
exec "$@"
