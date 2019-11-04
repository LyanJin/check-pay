#!/usr/bin/env bash

docker push payfornow/flask_base:v1.0
docker push payfornow/flask_app:v1.0
docker push payfornow/nginx_backoffice:v1.0
docker push payfornow/nginx_cashier:v1.0
docker push payfornow/nginx_callback:v1.0
