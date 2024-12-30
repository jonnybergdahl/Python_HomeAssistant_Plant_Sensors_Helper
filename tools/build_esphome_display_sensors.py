import secrets
from homeassistant_api import Client
from pprint import pprint
from collections import defaultdict
import requests
import json

HA_URL = secrets.HA_URL
HA_TOKEN = secrets.HA_TOKEN
HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}


def output_esphome_font():
    """
    Print the Esphome font configuration.
    """
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
    """
    Print the Esphome sensor configuration for the given plant entity.

    :param plant_entity: The plant entity to create the sensor configuration for.
    """
    print("  # -------------------------------")
    print(f"  # {plant_entity.state.attributes['friendly_name']}")
    print(f"  - platform: homeassistant")
    print(f"    id: {plant_entity.slug}_moisture")
    print(f"    entity_id: {plant_entity.entity_id}")
    print(f"    attribute: moisture_status")
    print(f"    internal: true")

    if plant_entity.state.attributes['conductivity_status'] is not None:
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
    """
    Print the initial part of the Esphome lambda function configuration.
    """
    print('    lambda: |-')
    print('      auto index = 0;')
    print('      DisplayHelper::renderFrame(&it, id(bold_font), id(esptime));')
    print('      DisplayHelper::renderCaption(&it, index++, id(bold_font), "Flowers");')
    print()


def output_esphome_lambda_line(plant_entity):
    """
    Print a line of the Esphome lambda function configuration for the given plant entity.

    :param plant_entity: The plant entity to create the lambda function line for.
    """
    if plant_entity.state.attributes['conductivity_status'] is not None:
        print(f"      DisplayHelper::renderPlantLine(&it, index++, id(normal), id(mdi_font), id({plant_entity.slug}_moisture), id({plant_entity.slug}_conductivity), id({plant_entity.slug}_name));")
    else:
        print(f"      DisplayHelper::renderMinPlantLine(&it, index++, id(normal), id(mdi_font), id({plant_entity.slug}_moisture), id({plant_entity.slug}_name));")


def get_area_name(entity_name):
    query = {
        "template": f"{{{{ area_name('plant.{entity_name}') }}}}"
    }
    body = json.dumps(query)
    area_response = requests.post(f"{HA_URL}/api/template", headers=HEADERS, data=body)
    return area_response.text

def main():
    """
    Main function for the script.
    Sets up the client connection, and processes plants to output Esphome yaml.
    """
    client = Client(f"{secrets.HA_URL}/api", secrets.HA_TOKEN)
    entities = client.get_entities()
    plants = entities["plant"]

    # Sort entities by area
    plants_by_area = defaultdict(list)
    for entity_id in plants.entities:
        area = get_area_name(entity_id)
        entity = plants.entities[entity_id]
        plants_by_area[area].append(entity)

    sorted_areas = list(plants_by_area.keys())
    sorted_areas.sort()
    for area_name in sorted_areas:
        print("  # ===============================")
        print(f"  # CYD setup for {area_name}")
        print("  # ===============================")

        output_esphome_font()
        for plant_entity in plants_by_area[area_name]:
            output_esphome_sensor(plant_entity)

        output_esphome_lambda()
        for plant_entity in plants_by_area[area_name]:
            output_esphome_lambda_line(plant_entity)


if __name__ == "__main__":
    main()