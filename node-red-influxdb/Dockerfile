FROM nodered/node-red:latest

# Install Node-RED InfluxDB nodes
RUN npm install node-red-contrib-influxdb

# Copy the flow configuration
COPY flows.json /data/flows.json

# Expose Node-RED's default port
EXPOSE 1880

# Set the default command with a wait script
# CMD ["sh", "-c", "while ! nc -z influxdb 8086; do sleep 1; done; npm start"]
CMD ["npm", "start"]
