#!/usr/bin/env bash

docker run --name flask_app -it -d -p 8000:8000 test/flask_app:v1.0
