# Python_HomeAssistant_Plant_Sensors

This repo contains helper scripts for keeping track of my plants in Home Assistant.

I am using the replacement Plant integration found here: [homeassistant-plant](https://github.com/Olen/homeassistant-plant),
together with the [MiFlora integration](https://www.home-assistant.io/integrations/xiaomi_ble/) 
and my [Growcube integration](https://github.com/jonnybergdahl/HomeAssistant_Growcube_Integration). 

I use [Mushroom Template card](https://github.com/piitaya/lovelace-mushroom) for my dashboards.

## secrets.py

To add your application secrets, create a file called `my_serets.py` in the `tools` folder and add the following.

```
HA_HOST = "<Home Assistant IP address or host name>"
HA_PORT = <Home Assistant port number>
HA_TOKEN = "<Your long lived Home Asistant token>"
```

## Tools

### build_mushroom_templates.py

This script creates Mushroom template card YAML file for use in a dashboard. It uses the
Home Assistant websocket API to extract all plant devices, sorts them by area and outputs
Mushroom card yaml.

Execute the script.

```bash
python3 build_mushroom_templates.py
```

Edit your dashboard, switch to yaml mode, and copy relevant parts of the output. 

```yaml
#============================
# Gästrum
#============================
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Gästrum
  - type: custom:mushroom-template-card
    entity: plant.gastrum_aloe_vera
    primary: Gästrum Aloe Vera
    picture: "{{ state_attr(entity, 'entity_picture') }}"
    secondary: >
      {% set sensor_name = entity.split('.')[1] %}
      {% set sensor = state_attr('sensor.gastrum_aloe_vera_soil_moisture', 'external_sensor') %}
      {% set battery = sensor.replace('moisture', 'battery') %}
      {% if state_attr(entity, 'moisture_status') == 'ok'  %} 💧{% else %} 🩸{% endif %}
      {{ states('sensor.gastrum_aloe_vera_soil_moisture', with_unit=True) }} - 
      {% if state_attr(entity, 'conductivity_status') == 'ok'  %} 🌿{% else %} 🌱{% endif %}
      {{ states('sensor.gastrum_aloe_vera_conductivity', with_unit=True) }}
      {% if has_value(battery) %} - 
      {% if states(battery) | int > 15 %} 🔋 {% else %} 🪫 {% endif %}
      {{ states(battery, with_unit=True) }} {% endif %}
      ({{ relative_time(states[entity].last_updated) }})
    badge_icon: |
      {% if is_state_attr(entity, 'moisture_status', 'ok') %} mdi:water {% else %} mdi:water-alert {% endif %}
    badge_color: |
      {% if is_state_attr(entity, 'moisture_status', 'ok') %} green {% else %} red {% endif %}
```

The result looks like this.

![Mushroom template sample](/assets/dashboard.png)

The top item shows a MiFlora backed Plant entity.

 - Humidity
 - Conductivity
 - Battery percentage
 - Last update

The bottom item shows a Growcube backed entity.

 - Humidity
 - Water empty status
 - Last update

### build_esphome_display_sensors.py

_Work in progress!_

This script creates ESPHome file that displays plants states on a CYD display.

It uses my [DisplayHelper library](https://github.com/jonnybergdahl/ESPHome_DisplayHelper), this needs to be installed in the `esphome` folder of your Home Assistant system.


