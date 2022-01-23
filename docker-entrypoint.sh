#!/bin/bash -x

python manage.py migrate  || exit 1
exec "$@"