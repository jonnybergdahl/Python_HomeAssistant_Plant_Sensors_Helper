# Python_HomeAssistant_Plant_Sensors

This repo contains helper scripts for keeping track of my plants in Home Assistant.

## secrets.py

To add your application secrets, create a file called `serets.py` in the `tools` folder and add the following.

```
HA_URL = "<Home Assistant URL>"
HA_TOKEN = "<Your long lived Home Asistant token>"
```

## Tools

### build_esphome_display_sensors.py

This script creates ESPHome file that displays plants states on a CYD display.

It uses my [DisplayHelper library](https://github.com/jonnybergdahl/ESPHome_DisplayHelper), this needs to be installed in the `esphome` folder of your Home Assistant system.

### build_mushroom_templates.py

This script creates Mushroom template card YAML file.