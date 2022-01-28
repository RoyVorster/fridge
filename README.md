# Fridge control system
## ESP32 side
- MQTT publisher
- MQTT subscriber for control inputs

## Server side
- MQTT broker
- Store data in timescaleDB
- VPN tunnel with VPS running really crappy front-end
- Frequency + lo/hi temperature estimation
    - Predict when to turn on/off
