#!/bin/bash
set -e

run_migrations() {
    python /project/app/manage.py shell < /wait_for_postgres.py
    python /project/app/manage.py migrate
}

if [ "$1" = 'local' ]; then
    run_migrations &&
    python /project/app/manage.py collectstatic --noinput
    exec python /project/app/manage.py runserver 0.0.0.0:8000

elif [ "$1" = 'debug' ]; then
    exec tail -f /dev/null

fi
