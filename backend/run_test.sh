#!/usr/bin/env bash

# 创建sqlites目录,测试环境sqlite使用
if [ ! -d "sqlites" ]; then
    echo "mkdir sqlites"
    mkdir sqlites
fi

# 单元测试的环境变量
export UNIT_TEST=True

nosetests -v --with-coverage --cover-package=app