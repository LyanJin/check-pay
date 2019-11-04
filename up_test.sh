#!/usr/bin/env bash

docker-compose -f docker-compose-test.yml up -d --no-deps
#docker-compose -f docker-compose-test.yml build
#docker-compose -f docker-compose-test.yml --up build
#docker-compose -f docker-compose-test.yml build nginx-cashier
#docker-compose -f docker-compose-test.yml build cashier
