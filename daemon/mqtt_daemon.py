import paho.mqtt.client as mqtt
import struct
import time

from db_helpers import execute_query

# MQTT Broker
host = 'localhost'
port = 1883
topic = 'fridge/temperature'

# Buffering and averaging
local_buffer, local_buffer_counter, t_buffer = 0, 0, 0
dt = 5

temperature_sensor_id = 0

def on_connect(client, userdata, flags, respons_code):
    client.subscribe(topic)

def on_message(client, userdata, msg):
    global t_buffer, local_buffer, local_buffer_counter

    temperature_msg = struct.unpack('f', msg.payload)[0]
    t = time.time()
    buffer_diff = t - t_buffer - dt
    if buffer_diff > 0:
        local_buffer_counter += buffer_diff
        local_buffer += buffer_diff*temperature_msg

        temperature = local_buffer/local_buffer_counter

        local_buffer = (1 - buffer_diff)*temperature_msg
        local_buffer_counter = (1 - buffer_diff)
        t_buffer = t

        query = '''
            INSERT INTO fridge_data VALUES (%s, NOW(), %s);
        '''
        execute_query(query, (temperature_sensor_id, temperature))
    else:
        local_buffer += temperature_msg
        local_buffer_counter += 1

if __name__=='__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port=port, keepalive=60)
    client.loop_forever()

