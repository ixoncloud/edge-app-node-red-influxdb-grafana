#!/bin/bash

# Output executed commands and stop on errors.
set -e -x

# Uncomment the following line should the edge gateway have been
# given a different IP address.
# docker buildx rm secure-edge-pro;

# Create and initialize the build environment.
docker buildx create --name secure-edge-pro \
                     --config buildkitd-secure-edge-pro.toml
docker buildx use secure-edge-pro

# Navigate to the influxdb directory and build the influxdb image
cd influxdb/
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/influxdb:latest --push .
cd ..

# Navigate to the grafana directory and build the grafana image with no cache
cd grafana/
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/grafana:latest --no-cache --push .
cd ..

# Navigate to the nodered directory and build the node-red-influxdb image
cd nodered/
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/node-red-influxdb:latest --push .
cd ..

# Navigate to the download-influxdb-backup directory and build the download-influxdb-backup image
cd download-influxdb-backup/
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/download-influxdb-backup:latest --push .
cd ..
