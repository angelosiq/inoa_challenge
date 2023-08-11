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

elif [ "$1" = 'celery-local' ]; then
    shift
    export PYTHONPATH='/app'
    echo "RUNNING CELERY WITH DEBUGPY AT localhost:6900"
    python -m debugpy --listen 0.0.0.0:6900 -m celery -A celery_worker worker --beat -E -l INFO

fi
