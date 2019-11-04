#!/usr/bin/env bash

echo "begin to exec entry point script for nginx"

chdir '/etc/nginx/conf.d/'
echo `pwd`

# 文件不存在直接退出
if [ ! -f "default.conf.tpl" ]; then
  echo "default.conf.tpl not exist"
  exit 1;
fi

echo "FLASK_ENV: $FLASK_ENV"
echo "NGINX_PORT: $NGINX_PORT"
echo "NGINX_HOST: $NGINX_HOST"
echo "BACKEND_PORT: $BACKEND_PORT"
echo "BACKEND_HOST: $BACKEND_HOST"

# 环境变量替换
sed -e "s/{NGINX_PORT}/$NGINX_PORT/g" \
    -e "s/{NGINX_HOST}/$NGINX_HOST/g" \
    -e "s/{BACKEND_PORT}/$BACKEND_PORT/g" \
    -e "s/{BACKEND_HOST}/$BACKEND_HOST/g" \
    default.conf.tpl > default.conf

cat default.conf

# 执行CMD
# 如果docker run时没有指定CMD，那么会使用dockerfile中的CMD
# 如果docker run时指定了CMD，那么dockerfile中的CMD会被忽律
echo "$@"
exec "$@"
