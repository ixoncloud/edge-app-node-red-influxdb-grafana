# Navigate to the influxdb directory and build the influxdb image
cd influxdb/
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/influxdb:latest --push .
cd ..

# Navigate to the grafana directory and build the grafana image with no cache
cd grafana/
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/grafana:latest --no-cache --push .
cd ..

# Navigate to the node-red directory and build the nodered image
cd nodered
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/node-red-influxdb:latest --push .
cd ..

# Navigate to the download-influxdb-to-csv directory and build the download-influxdb-to-csv image
cd download-influxdb-backup
docker buildx build --platform linux/arm64/v8 --tag 192.168.140.1:5000/download-influxdb-backup:latest --push .
cd ..
