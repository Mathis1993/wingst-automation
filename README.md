# wingst-automation

## Purpose
This repository aims to control a heat pump based on current power production of a photovoltaic system.
When a certain amount of power is produced, the heat pump should increase the flow temperature used to heat water for
the heating system (radiators).
When the power production drops, the flow temperature should be decreased again.

## Structure
The repository is structured as follows:
- `smartthings`: Contains a wrapper around the SmartThings API to control the heat pump
- `wingst`: Contains the main logic to control the heat pump based on the power production of the photovoltaic system

## Resources
- [SmartThings API](https://developer.smartthings.com/docs/api/public)
  - https://api.smartthings.com/v1/devices
  - https://api.smartthings.com/v1/capabilities/custom.thermostatSetpointControl/1
- [Tibber API](https://developer.tibber.com/docs/overview)
  - Nice wrapper: https://github.com/BeatsuDev/tibber.py
