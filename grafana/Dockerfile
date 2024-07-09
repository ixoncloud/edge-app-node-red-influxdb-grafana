# Use the specified Grafana image
FROM grafana/grafana:10.4.1-ubuntu

# Set Grafana admin user and password
ENV GF_SECURITY_ADMIN_USER=admin \
    GF_SECURITY_ADMIN_PASSWORD=admin \
    GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource \ 
    DOCKER_INFLUXDB_INIT_ORG="myorg" \
    DOCKER_INFLUXDB_INIT_BUCKET="mybucket" \
    DOCKER_INFLUXDB_INIT_ADMIN_TOKEN="myadmintoken" 

# Copy provisioning files for datasources and dashboards into the container
COPY ./provisioning/datasources/* /etc/grafana/provisioning/datasources/
COPY ./provisioning/dashboards/* /etc/grafana/provisioning/dashboards/

# Copy initial dashboard JSON files into the container
COPY ./dashboards/* /var/lib/grafana/dashboards/

# Mark the volume for Grafana data to ensure data persistence
VOLUME /var/lib/grafana

# Expose Grafana's default port
EXPOSE 3000

# The base image has a suitable entrypoint for running Grafana.
