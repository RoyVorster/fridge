from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import paho.mqtt.client as mqtt
import struct

from db import *
from analysis import get_data, get_command

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# paho MQTT setup
HOST, PORT, TOPIC = 'localhost', 1883, 'fridge/temperature'

N_REFRESH = 1000 # Refresh DB every 1000 new datapoints
counter = 0

@app.route('/data', methods=['POST'])
def get_data_api():
    interval = request.json['interval']
    n_points = request.json['n_points']
    sensor_id = request.json['sensor_id']

    time, data = get_data(interval=interval, n_points=n_points, sensor_id=sensor_id)
    message = {'time': list(time), 'data': list(data)}

    return jsonify(message)

@app.route('/command', methods=['POST'])
def get_command_api():
    t_sleep = request.json['t_sleep']

    time, data = get_data(t_back='12 hours', interval='2 minutes')
    message = {'command': get_command(time, data, t_sleep=t_sleep)}

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

