#!/usr/bin/env bash

# 创建sqlites目录,测试环境sqlite使用
if [ ! -d "sqlites" ]; then
    echo "mkdir sqlites"
    mkdir sqlites
fi

## 编译之前进行单元测试
#nosetests -v --with-coverage --cover-package=app
#
#test_rst=$?
#
#if test $test_rst -ne 0; then
#    # nosetests测试失败，返回值不等于0，不再往下执行
#    echo "单元测试返回 $test_rst, 测试不通过"
#    exit 1
#fi
#
#unset test_rst

# 删除旧的镜像
docker rmi payfornow/flask_app:v1.0

# 编译
docker build -f ./Dockerfile.app -t payfornow/flask_app:v1.0 .

# 推送到gitlab
docker push payfornow/flask_app:v1.0

## 标签ECR
#docker tag payfornow/flask_app:v1.0 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/flask_app:v1.0
#
## 推送到ECR
#docker push 609003501951.dkr.ecr.ap-east-1.amazonaws.com/payfornow/flask_app:v1.0
