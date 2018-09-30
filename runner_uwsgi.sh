#!/usr/bin/env bash

#uwsgi --socket 127.0.0.1:8080 --wsgi-file server.py --callable app --processes 4 --threads 2   #use socket
#uwsgi --http 127.0.0.1:8080 --wsgi-file server.py --callable app --processes 4 --threads 2    #use http
uwsgi --ini ./uwsgi.ini --callable app
