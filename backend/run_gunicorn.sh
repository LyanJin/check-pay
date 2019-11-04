#!/usr/bin/env bash

#Gunicorn with gevent async worker
#gunicorn server:app -k gevent --worker-connections 1000

#Gunicorn 1 worker 12 threads:
#gunicorn server:app -w 1 --threads 12

#Gunicorn with 4 workers (multiprocessing):
#gunicorn server:app -w 4

gunicorn --config ./gunicorn.py app.main:flask_app
