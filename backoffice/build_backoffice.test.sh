#!/usr/bin/env bash

# 删除旧的镜像
docker rmi payfornow/nginx_backoffice_test:v1.0

# 编译
docker build -f ./Dockerfile.backoffice.test -t payfornow/nginx_backoffice_test:v1.0 .

# 推送
docker push payfornow/nginx_backoffice_test:v1.0

## 标签
#docker tag payfornow/nginx_backoffice_test:v1.0 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/nginx_backoffice_test:v1.0
#
## 推送
#docker push 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/nginx_backoffice_test:v1.0
