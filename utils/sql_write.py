import paho.mqtt.client as mqtt
import struct
import time

from db_helpers import execute_query

# MQTT Broker
host = 'localhost'
port = 1883
topic = 'fridge/temperature'

# Buffering and averaging
t_buffer, n_counter = 0, 0
n_average = 5

temperature_sensor_id = 0


def on_connect(client, userdata, flags, respons_code):
    client.subscribe(topic)


def on_message(client, userdata, msg):
    global t_buffer, n_counter

    temperature_msg = struct.unpack('f', msg.payload)[0]
    if n_counter >= n_average + 1:
        temperature = (t_buffer + temperature_msg)/n_average
        n_counter = 0

        query = '''
            INSERT INTO fridge_data VALUES (%s, NOW(), %s);
        '''
        execute_query(query, (temperature_sensor_id, temperature))
    else:
        t_buffer += temperature_msg
        n_counter += 1


if __name__=='__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port=port, keepalive=60)
    client.loop_forever()

