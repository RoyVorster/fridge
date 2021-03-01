import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO

import struct
import paho.mqtt.client as mqtt


eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)


# Simple paho MQTT setup
host = 'eltigre'
port = 1883
topic = 'fridge/temperature'


@app.route('/')
def index():
    return render_template('index.html')


# PAHO event handlers
def on_connect(client, userdata, flags, respons_code):
    client.subscribe(topic)


def on_message(client, userdata, msg):
    temperature = struct.unpack('f', msg.payload)[0]
    socketio.emit('temperature', {'data': temperature})


if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port=port, keepalive=60)
    client.loop_start()

    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)

