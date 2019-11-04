#!/usr/bin/env bash

# 清理docker:
# 已停止的容器
# 未被任何容器使用的卷
# 未被任何容器所关联的网络
# 所有悬空的镜像
# docker system prune

# 一并清除所有未被使用的镜像和悬空镜像
#docker system prune -a

# 删除异常停止的docker容器
docker rm `docker ps -a | grep Exited | awk '{print $1}'`

# 删除名称或标签为none的镜像
docker rmi -f  `docker images | grep '<none>' | awk '{print $3}'`
