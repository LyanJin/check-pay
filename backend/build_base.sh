#!/usr/bin/env bash

# flask环境基础镜像,当应用的依赖环境Pipfile发生变化时，就要重新编译

# 删除旧的镜像
docker rmi payfornow/flask_base:v1.0

# 编译
docker build --no-cache -f ./Dockerfile.base -t payfornow/flask_base:v1.0 .

# 推送 gitlab
docker push payfornow/flask_base:v1.0

## 标签 ecr
#docker tag payfornow/flask_base:v1.0 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/flask_base:v1.0
#
## 推送 ecr
#docker push 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/flask_base:v1.0
