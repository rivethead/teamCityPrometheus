#!/bin/bash


printf "Starting Prometheus ...\n"

CONFIG_FILE="`pwd`/prometheus.yml"

docker run -d -p 9090:9090 \
    -v ${CONFIG_FILE}:/etc/prometheus/prometheus.yml \
    --network=host \
    prom/prometheus \
    --config.file=/etc/prometheus/prometheus.yml


printf "\nstarted \n"

printf "Starting Grafana ...\n"

docker run -d -p 3000:3000 --network=host grafana/grafana

printf "\nstarted \n"

printf "Starting push gateway ...\n"

docker run -d -p 9091:9091 --network=host prom/pushgateway

printf "\nstarted \n"
