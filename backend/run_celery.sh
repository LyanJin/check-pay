#!/usr/bin/env bash

celery -A app.main:flask_celery worker
