from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import paho.mqtt.client as mqtt
import struct

from db import *

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# paho MQTT setup
HOST, PORT, TOPIC = 'localhost', 1883, 'fridge/temperature'

N_REFRESH = 1000 # Refresh DB every 1000 new datapoints
counter = 0

@app.route('/data', methods=['POST'])
def get_data():
    interval = request.json['interval']
    n_points = request.json['n_points']
    sensor_id = request.json['sensor_id']

    query = '''
        SELECT t, d FROM (
            SELECT time_bucket(%s, time) AS t, avg(data) as d
            FROM fridge.data
            WHERE sensor_id = %s
            GROUP BY t
            ORDER BY t DESC LIMIT %s
        ) tt ORDER BY t ASC;
    '''
    values = (interval, sensor_id, n_points)
    res = exec_query(query, values)
    time, data  = [r[0] for r in res], [r[1] for r in res]

    message = {'time': time, 'data': data}
    return jsonify(message)

def cleanup_db():
    query = '''DELETE FROM fridge.data WHERE time < NOW() - INTERVAL '2 weeks';'''
    exec_query(query)

# PAHO event handlers
def on_connect(client, userdata, flags, respons_code):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global counter

    temperature = struct.unpack('f', msg.payload)[0]
    counter += 1

    query = '''
        INSERT INTO fridge.data (time, data, sensor_id)
        VALUES (NOW(), %s, 0)
    '''
    exec_query(query, (temperature,))

    # Delete old datapoints every once in a while
    if counter > N_REFRESH:
        counter = 0
        cleanup_db()

if __name__ == '__main__':
    init_db()

    # Init MQTT client
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(HOST, port=PORT, keepalive=60)
    client.loop_start()

    # Start flask app
    app.run(host='0.0.0.0', port=5001)

