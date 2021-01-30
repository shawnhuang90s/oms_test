#!/usr/bin/env bash
pkill -9 uwsgi
uwsgi --ini uwsgi.ini
ps -ef | grep uwsgi