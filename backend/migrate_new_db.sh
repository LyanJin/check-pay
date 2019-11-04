#!/usr/bin/env bash

python manage.py db heads
python manage.py db stamp rev_id
python manage.py db migrate
