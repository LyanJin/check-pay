# COPY 拷贝文件到docker上下文环境，每次执行都会创建新的镜像层。
# RUN 执行命令并创建新的镜像层，RUN 经常用于安装软件包。
# CMD 设置容器启动后默认执行的命令及其参数，但 CMD 能够被 docker run 后面跟的命令行参数替换。
# ENTRYPOINT 配置容器启动前必须运行的命令。
FROM payfornow/flask_base:v1.0

LABEL maintainer="kevin <nullclard@gmail.com>"

WORKDIR /www/

COPY ./ ./

# 入口脚本，在CMD执行之前执行
ENTRYPOINT ["sh", "entrypoint_app.sh"]

# 用gunicorn启动flask应用
CMD gunicorn --config gunicorn.py app.main:flask_app
