#!/usr/bin/env bash

#uwsgi --socket 127.0.0.1:8080 --wsgi-file server.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191

uwsgi --ini /home/jrg/Documentos/python/uf_beta/uwsgi.ini
