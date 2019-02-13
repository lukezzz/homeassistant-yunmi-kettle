# homeassistant-yunmi-kettle

This is a custom component for hass to integrate the yunmi kettle:
Model ID: yunmi.kettle.r3


Please follow the instructions on [Retrieving the Access Token](https://www.home-assistant.io/components/vacuum.xiaomi_miio/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

## Features
* Set water temperature 

## Setup

```yaml
# configuration.yaml

sensor:
  - platform: yunmi_kettle
    host: 192.168.98.105
    token: 17522738c1a979c1fcafafa44c7a9dec
    name: Yunmi Kettle

input_number:
  yunmi_kettle_set_temp:
    name: set temperature
    initial: 48
    min: 40
    max: 90
    step: 1
    unit_of_measurement: °C
    icon: mdi:water-pump
```

## Platform services

#### Service `sensor.set_kettle_temp`

Set the water temperature.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `temp`               |      yes | default is 48,  temperature range can be from 40°C to 90°C    |

## Automation
```
- id: kettle temperature setting
  alias: kettle temperature setting
  trigger:
  - entity_id: input_number.yunmi_kettle_set_temp
    platform: state
  action:
  - data_template:
      temp: '{{ states.input_number.yunmi_kettle_set_temp.state | int }}'
    service: sensor.set_kettle_temp
```
