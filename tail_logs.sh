#!/usr/bin/env bash

tail -f /tmp/backoffice_nginx/logs/* \
    /tmp/backoffice_web/logs/* \
    /tmp/callback_nginx/logs/* \
    /tmp/callback_web/logs/* \
    /tmp/cashier_nginx/logs/* \
    /tmp/cashier_web/logs/* \
    /tmp/configuration/logs/* \
    /tmp/scheduler/logs/*
