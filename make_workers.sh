#!/bin/bash
source ./report_env/bin/activate
supervisord -c ./supervisord.conf
rq-dashboard
# python ./report-dfms/src/watcher.py
