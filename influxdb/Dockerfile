# Use the InfluxDB Alpine image
FROM influxdb:2.7.5-alpine

# If you have initial setup scripts for InfluxDB, you can COPY them here.
# Example for copying a setup script (Adjust as necessary):
# COPY ./path/to/your/setup-script.sh /docker-entrypoint-initdb.d/

# InfluxDB options
ENV DOCKER_INFLUXDB_INIT_MODE=setup \
  DOCKER_INFLUXDB_INIT_USERNAME=myuser \
  DOCKER_INFLUXDB_INIT_PASSWORD=mystrongpassword \
  DOCKER_INFLUXDB_INIT_ORG=myorg \
  DOCKER_INFLUXDB_INIT_BUCKET=mybucket \
  DOCKER_INFLUXDB_INIT_RETENTION=1w \
  DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=myadmintoken \
  # Disable internet-dependent features
  INFLUXDB_REPORTING_DISABLED=true \
  INFLUXDB_HTTP_FLUX_LOG_ENABLED=false \
  DOCKER_INFLUXDB_INIT_MODE=setup \
  INFLUXDB_UI_DISABLED=false

# Create a custom influxdb.conf file
COPY ./influxdb.conf /etc/influxdb/influxdb.conf

# Define a volume for persistence. Adjust if you have a specific path in mind.
VOLUME /var/lib/influxdb

# Expose the port InfluxDB runs on
EXPOSE 8086
