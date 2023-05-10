import secrets
from homeassistant_api import Client
from pprint import pprint

#secrets = {
#    "HA_URL": "http://ha.bergdahl.local/api",
#    "HA_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZjYzYjc5NmM0MmM0YjI2OTUxY2M2NjdjOTQyZjViNSIsImlhdCI6MTY4MzcxMzM4NSwiZXhwIjoxOTk5MDczMzg1fQ.UJUN1R4cyHJKRhUzpxAeqsFU3z39oeKMYj96CTUe0TU"
#}

def output_esphome_font():
    print('font:')
    print('  - file: "fonts/arial.ttf"')
    print('    id: normal_font')
    print('    size: 16')
    print('    glyphs: "!\"%()+=,-_.:°0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ abcdefghijklmnopqrstuvwxyzåäö"')
    print('  - file: "fonts/arial-bold.ttf"')
    print('    id: bold_font')
    print('    size: 16')
    print('    glyphs: "!\"%()+=,-_.:°0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ abcdefghijklmnopqrstuvwxyzåäö"')
    print('  - file: "fonts/materialdesignicons-webfont.ttf"')
    print('    id: mdi_font')
    print("    glyphs: ")
    print('      - "\\U000F058C"  # mdi:water')
    print('      - "\\U000F058D"  # mdi:water-off')
    print('      - "\\U000F032A"  # mdi:leaf')
    print('      - "\\U000F12D9"  # mdi:leaf-off")')
    print()

def output_esphome_sensor(plant_entity):
    print(f"# {plant_entity.state.attributes['friendly_name']}")
    print(f"  - platform: homeassistant")
    print(f"    id: {plant_entity.slug}_moisture")
    print(f"    entity_id: {plant_entity.entity_id}")
    print(f"    attribute: moisture_status")
    print(f"    internal: true")

    print(f"  - platform: homeassistant")
    print(f"    id: {plant_entity.slug}_conductivity")
    print(f"    entity_id: {plant_entity.entity_id}")
    print(f"    attribute: conductivity_status")
    print(f"    internal: true")

    print(f"  - platform: homeassistant")
    print(f"    id: {plant_entity.slug}_name")
    print(f"    entity_id: {plant_entity.entity_id}")
    print(f"    attribute: friendly_name")
    print(f"    internal: true")
    print()

def output_esphome_lambda():
    print('    lambda: |-')
    print('      auto index = 0;')
    print('      DisplayHelper::renderFrame(&it, id(bold_font), id(esptime));')
    print('      DisplayHelper::renderCaption(&it, index++, id(bold_font), "Flowers");')
    print()

def output_esphome_lambda_line(plant_entity):
    print(f"      DisplayHelper::renderPlantLine(&it, index++, id(normal), id(mdi_font), id({plant_entity.slug}_moisture), id({plant_entity.slug}_conductivity), id({plant_entity.slug}_name));")
    

client = Client(f"{secrets.HA_URL}/api", secrets.HA_TOKEN)
entities = client.get_entities()
plants = entities["plant"]

output_esphome_font()

for plant_name in plants.entities:
    plant_entity = plants.entities[plant_name]
    output_esphome_sensor(plant_entity)

output_esphome_lambda()
for plant_name in plants.entities:
    plant_entity = plants.entities[plant_name]
    output_esphome_lambda_line(plant_entity)

