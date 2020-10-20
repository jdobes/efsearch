#!/bin/sh

cd $(dirname $0)

if [[ ! -z $1 ]]; then
    if [[ "$1" == "producer" ]]; then
        exec python3 -m producer.producer
    elif [[ "$1" == "consumer" ]]; then
        exec python3 -m consumer.consumer
    fi
fi

echo "Please specify service name as the first argument."
