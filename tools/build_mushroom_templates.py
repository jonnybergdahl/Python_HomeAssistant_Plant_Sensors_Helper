import secrets
from homeassistant_api import Client
from pprint import pprint
from collections import defaultdict
import requests
import json

HA_URL = secrets.HA_URL
HA_TOKEN = secrets.HA_TOKEN
HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

def output_mushroom_template(plant_entity):
    """
    Print the Mushroom template for the given plant entity.

    :param plant_entity: The plant entity to create the template for.
    """
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
    # Get plant entities
    client = Client(f"{secrets.HA_URL}/api", secrets.HA_TOKEN)
    entities = client.get_entities()
    plants = entities["plant"]

    # Sort entities by area
    plants_by_area = defaultdict(list)
    for entity_id in plants.entities:
        area = get_area_name(entity_id)
        entity = plants.entities[entity_id]
        plants_by_area[area].append(entity)
    #

    sorted_areas = list(plants_by_area.keys())
    sorted_areas.sort()
    for area_name in sorted_areas:
        for entity in plants_by_area[area_name]:
            output_mushroom_template(entity)


if __name__ == "__main__":
    main()