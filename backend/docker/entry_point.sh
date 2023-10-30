#!/bin/bash

# Tell python not to buffer any output to stdout and stderr. Not setting this makes any debugging almost
# impossible
export PYTHONUNBUFFERED=1

echo "starting gunicorn"
# Run gunicorn. $USER and $PORT are set in the Dockerfile
exec gunicorn --config /etc/gunicorn.conf.py \
--access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(l)s' \
objectiv_backend.wsgi
