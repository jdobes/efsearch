#!/bin/sh

cd $(dirname $0)

if [[ ! -z $1 ]]; then
    if [[ "$1" == "db-admin" ]]; then
        exec python3 -m db_admin.db_admin
    elif [[ "$1" == "scheduler" ]]; then
        exec python3 -m scheduler.scheduler
    elif [[ "$1" == "fetcher" ]]; then
        exec python3 -m fetcher.fetcher
    fi
fi

echo "Please specify service name as the first argument."
