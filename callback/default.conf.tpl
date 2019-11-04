server {
    listen      {NGINX_PORT};
    server_name {NGINX_HOST};

    #charset koi8-r;
    access_log  /var/log/nginx/{BACKEND_HOST}.access.log  main;
    access_log on;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    location ~ /api/ {
        if ( $http_x_forwarded_proto = http ){
            # 非https拒绝访问
            return 403;
        }
        proxy_pass                          http://{BACKEND_HOST}:{BACKEND_PORT};
        proxy_send_timeout                  1800;
        proxy_read_timeout                  1800;
        proxy_connect_timeout               1800;
        client_max_body_size                2048m;
        proxy_http_version                  1.1;
        proxy_set_header  Host              $http_host;   # required for docker client's sake
        proxy_set_header  X-Real-IP         $remote_addr; # pass on real client's IP
        proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Proto $scheme;
    }

    location ~* health/check$ {
        # 健康检查用http
        proxy_pass                          http://{BACKEND_HOST}:{BACKEND_PORT};
        proxy_send_timeout                  1800;
        proxy_read_timeout                  1800;
        proxy_connect_timeout               1800;
        client_max_body_size                2048m;
        proxy_http_version                  1.1;
        proxy_set_header  Host              $http_host;   # required for docker client's sake
        proxy_set_header  X-Real-IP         $remote_addr; # pass on real client's IP
        proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Proto $scheme;
    }

    location ~ /(doc|swaggerui)/ {
        #allow 103.119.131.7;    # 运营办公室IP
        #allow 130.105.213.136;  # panda家里IP
        #allow 112.209.119.254;  # kb 4318
        #deny all;

        auth_basic "需要鉴权";
        auth_basic_user_file /etc/nginx/conf.d/htpasswd;

        proxy_pass                          http://{BACKEND_HOST}:{BACKEND_PORT};
        proxy_send_timeout                  1800;
        proxy_read_timeout                  1800;
        proxy_connect_timeout               1800;
        client_max_body_size                2048m;
        proxy_http_version                  1.1;
        proxy_set_header  Host              $http_host;   # required for docker client's sake
        proxy_set_header  X-Real-IP         $remote_addr; # pass on real client's IP
        proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Proto $scheme;
    }

}
