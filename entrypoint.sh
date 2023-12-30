#!/bin/sh

cd $(dirname $0)

if [[ ! -z $1 ]]; then
    if [[ "$1" == "db-admin" ]]; then
        exec python3 -m backend.db_admin.db_admin
    elif [[ "$1" == "scheduler" ]]; then
        exec python3 -m backend.scheduler.scheduler
    elif [[ "$1" == "fetcher" ]]; then
        exec python3 -m backend.fetcher.fetcher
    elif [[ "$1" == "frontend" ]]; then
        exec gunicorn -w 4 --bind=0.0.0.0:8000 frontend.efsearch
    fi
fi

echo "Please specify service name as the first argument."
