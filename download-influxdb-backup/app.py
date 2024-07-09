from flask import Flask, Response, stream_with_context, request
from flask_socketio import SocketIO, emit
from influxdb_client import InfluxDBClient
import os
import logging
import csv
import io
from datetime import datetime, timedelta
import tarfile

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# InfluxDB connection details from environment variables
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
DOCKER_INFLUXDB_INIT_ADMIN_TOKEN = os.getenv(
    "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
INFLUXDB_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
INFLUXDB_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")

client = InfluxDBClient(
    url=INFLUXDB_URL, token=DOCKER_INFLUXDB_INIT_ADMIN_TOKEN, org=INFLUXDB_ORG)


@app.route('/')
def home():
    return '''
        <html>
            <body>
                <h1>Download InfluxDB Metrics</h1>
                <form id="downloadForm" action="/download" method="post">
                    <label for="time_value">Time Value:</label>
                    <input type="number" id="time_value" name="time_value" required>
                    <label for="time_unit">Time Unit:</label>
                    <select id="time_unit" name="time_unit" required>
                        <option value="hours">Hours</option>
                        <option value="days">Days</option>
                        <option value="weeks">Weeks</option>
                        <option value="months">Months</option>
                    </select>
                    <button type="submit">Download to CSV</button>
                </form>
                <br>
                <h1>Backup InfluxDB Data</h1>
                <form id="backupForm" action="/backup" method="post">
                    <button type="submit">Download Backup</button>
                </form>
                <div id="status"></div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.min.js"></script>
                <script>
                    var socket = io();
                    document.getElementById('downloadForm').onsubmit = function(event) {
                        event.preventDefault();
                        document.getElementById('status').innerHTML = 'Starting download...';

                        socket.on('status_update', function(msg) {
                            document.getElementById('status').innerHTML = msg.data;
                        });

                        var xhr = new XMLHttpRequest();
                        xhr.open('POST', '/download', true);
                        xhr.responseType = 'blob';

                        xhr.onload = function() {
                            if (xhr.status === 200) {
                                var a = document.createElement('a');
                                var url = window.URL.createObjectURL(xhr.response);
                                a.href = url;
                                a.download = 'metrics.csv';
                                document.body.appendChild(a);
                                a.click();
                                window.URL.revokeObjectURL(url);
                                document.getElementById('status').innerHTML = 'Download complete!';
                            } else {
                                document.getElementById('status').innerHTML = 'Download failed!';
                            }
                        };

                        var formData = new FormData(document.getElementById('downloadForm'));
                        xhr.send(formData);
                    };

                    document.getElementById('backupForm').onsubmit = function(event) {
                        event.preventDefault();
                        document.getElementById('status').innerHTML = 'Starting backup...';

                        socket.on('status_update', function(msg) {
                            document.getElementById('status').innerHTML = msg.data;
                        });

                        var xhr = new XMLHttpRequest();
                        xhr.open('POST', '/backup', true);
                        xhr.responseType = 'blob';

                        xhr.onload = function() {
                            if (xhr.status === 200) {
                                var a = document.createElement('a');
                                var url = window.URL.createObjectURL(xhr.response);
                                a.href = url;
                                a.download = 'influxdb_backup.tar';
                                document.body.appendChild(a);
                                a.click();
                                window.URL.revokeObjectURL(url);
                                document.getElementById('status').innerHTML = 'Backup complete!';
                            } else {
                                document.getElementById('status').innerHTML = 'Backup failed!';
                            }
                        };

                        xhr.send();
                    };
                </script>
            </body>
        </html>
    '''


@app.route('/download', methods=['POST'])
def download():
    def generate():
        logging.debug("Starting CSV generation")

        # Get time value and unit from the form
        time_value = int(request.form['time_value'])
        time_unit = request.form['time_unit']

        # Calculate the start time based on the provided time range
        end_time = datetime.utcnow()
        if time_unit == 'hours':
            start_time = end_time - timedelta(hours=time_value)
        elif time_unit == 'days':
            start_time = end_time - timedelta(days=time_value)
        elif time_unit == 'weeks':
            start_time = end_time - timedelta(weeks=time_value)
        elif time_unit == 'months':
            # Approximate to 30 days per month
            start_time = end_time - timedelta(days=time_value * 30)

        # Prepare CSV writer
        output = io.StringIO()
        writer = csv.writer(output)

        # Write CSV header
        header_written = False
        total_records = 0

        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
        '''
        logging.debug(f"Executing query for range: {start_time} to {end_time}")
        result = client.query_api().query(query, org=INFLUXDB_ORG)

        for table in result:
            for record in table.records:
                if not header_written:
                    writer.writerow(record.values.keys())
                    output.seek(0)
                    yield output.read()
                    output.truncate(0)
                    header_written = True

                writer.writerow(record.values.values())
                total_records += 1

                if total_records % 1000 == 0:
                    output.seek(0)
                    yield output.read()
                    output.truncate(0)
                    logging.debug(f"Processed {total_records} records so far")

        # Send any remaining data in the buffer
        output.seek(0)
        yield output.read()
        logging.debug(f"CSV generation complete. Total records processed: {
                      total_records}")

        socketio.emit('status_update', {
                      'data': f"CSV generation complete. Total records processed: {total_records}"})

    logging.debug("Returning response")
    return Response(
        stream_with_context(generate()),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=metrics.csv'}
    )


@app.route('/backup', methods=['POST'])
def backup():
    def generate_backup():
        logging.debug("Starting backup generation")
        backup_dir = '/var/lib/influxdb2'

        # Create an in-memory tarball
        with io.BytesIO() as tar_stream:
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))

            tar_stream.seek(0)
            while chunk := tar_stream.read(8192):
                yield chunk

        logging.debug("Backup generation complete")
        socketio.emit('status_update', {'data': "Backup generation complete."})

    logging.debug("Returning backup response")
    return Response(
        stream_with_context(generate_backup()),
        mimetype='application/octet-stream',
        headers={'Content-Disposition': 'attachment;filename=influxdb_backup.tar'}
    )


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80)
