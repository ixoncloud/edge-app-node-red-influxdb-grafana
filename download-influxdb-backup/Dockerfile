# Use an official Python runtime as a parent image
FROM python:3.12.5-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV DOCKER_INFLUXDB_INIT_ORG=myorg \
    DOCKER_INFLUXDB_INIT_BUCKET=mybucket \
    INFLUXDB_URL=http://influxdb:8086 \
    DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=myadmintoken

# Run app.py when the container launches
CMD ["python", "app.py"]
