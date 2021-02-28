import paho.mqtt.client as mqtt
import struct

# MQTT Broker
host = 'eltigre'
port = 1883
topic = 'fridge/temperature'

def on_connect(client, userdata, flags, respons_code):
    client.subscribe(topic)

def on_message(client, userdata, msg):
    temperature = struct.unpack('f', msg.payload)[0]
    print(f"Temperature: {temperature}")

if __name__=='__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port=port, keepalive=60)
    client.loop_forever()
