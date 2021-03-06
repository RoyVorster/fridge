# Fridge control system
## ESP32 side
- MQTT publisher
- MQTT subscriber for control inputs

## Broker side
- MQTT broker, store data in timescaledb database
- Fridge state- and parameter estimation
    - state: [temperature, power_on, door_open]
    - parameters: [thermal mass]
- With preset times - run predictive control loop to ensure at min/max bounds when fridge is required to turn on/off
