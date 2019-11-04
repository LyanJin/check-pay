FROM nginx:1.17.0-alpine

# 拷贝主配置文件
COPY nginx.conf /etc/nginx/nginx.conf
# 拷贝项目配置文件模板，模板会在entrypoint.sh里面再渲染出配置文件
COPY default.conf.tpl /etc/nginx/conf.d/
# 文档目录的访问密钥
COPY htpasswd /etc/nginx/conf.d/

# 拷贝入口脚本
WORKDIR /usr/local/bin/
COPY entrypoint.sh .
ENTRYPOINT ["sh", "entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]
