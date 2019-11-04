#!/usr/bin/env bash

# 删除旧的镜像
docker rmi payfornow/nodejs3:v1.0

# 编译
docker build -f ./Dockerfile.nodejs3 -t payfornow/nodejs3:v1.0 .

# 推送
docker push payfornow/nodejs3:v1.0

# 标签
docker tag payfornow/nodejs3:v1.0 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/nodejs3:v1.0

# 推送
docker push 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/nodejs3:v1.0
