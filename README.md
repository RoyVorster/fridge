# Fridge measurement + turn off when going to sleep
Compute manual turn on/off times for fridge to delay cycle such that I can sleep... There is an ESP32 in the fridge communicating with home RPI via MQTT and a [web front-end](http://koelkast.royvorster.nl/) running on a VPS communicating with the RPI via a wireguard VPN tunnel.

## ESP32 side
- MQTT publisher

## Server side
- MQTT broker
- Store data in postgres database (TimescaleDB)
- VPN tunnel with VPS running crappy front-end
- Estimate time to turn on/off to fall asleep in peace

