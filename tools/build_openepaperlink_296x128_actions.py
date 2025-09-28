import asyncio
from typing import List, Dict, Any

import my_secrets
from tools.home_assistant_websocket_client import HomeAssistantWebSocketClient

"""
Script for the Hanshow 296x128 tags
"""

def output_template_header(plant_entities: List[Dict[str, Any]]) -> None:
    """
    Outputs the header for the plant entities formatted as Esphome YAML.

    Args:
        plant_entities (List[Dict[str, Any]]): A list of dictionaries containing plant data.
            Each dictionary represents a plant entity and contains its metadata.

    Returns:
        None
    """
    area_name: str = plant_entities[0]['area_name']
    print(f"# ============================")
    print(f"# {area_name}")
    print(f"# ============================")
    print(f"action: open_epaper_link.drawcustom")
    print(f"data:")
    print(f"  background: white")
    print(f"  rotate: 0")
    print(f"  dither: 2")
    print(f"  ttl: 60")
    print(f"  payload:")

    # Background icon
    conditions = " and ".join([f"(state_attr('{pe['entity_id']}','moisture_status') == 'ok')" for pe in plant_entities])
    print(f"    - type: icon")
    print(f"      value: >-")
    print(f"        {{{{ 'thumbs-up-outline' if {conditions} else 'thumbs-down-outline' }}}}")
    print(f"      x: 148")
    print(f"      'y': >-")
    print(f"        {{{{ 180 if {conditions} else 64 }}}}")
    print(f"      size: 100")
    print(f"      anchor: mm")
    print(f"      color: red")

    # Time stamp
    print(f"    - type: text")
    print(f"      value: >-")
    print(f"        {{{{ now() | as_timestamp  | timestamp_custom(\"%Y-%m-%d %H:%M\", true) }}}}")
    print(f"      font: rcm.ttf")
    print(f"      x: 294")
    print(f"      y: 127")
    print(f"      size: 12")
    print(f"      color: black")
    print(f"      anchor: rd")


def output_mushroom_template(plant_entity: Dict[str, Any], index: int) -> None:
    """
    Outputs the detailed mushroom-template-card configuration for a plant entity.

    Args:
        plant_entity (Dict[str, Any]): A dictionary containing metadata for a single plant entity.
            It should include fields such as 'entity_id', 'name', and so on.

    Returns:
        None
    """
    entity_id: str = plant_entity['entity_id']
    name: str = plant_entity['name']
    sensor_name: str = entity_id.split('.')[1]
    y = 20 * (index + 1)
    print( "# --------------------------------------")
    print(f"# { name }")
    print( "# --------------------------------------")
    # Moisture
    print(f"    - type: icon")
    print(f"      value: >-")
    print(f"        {{{{ 'water' if state_attr('{plant_entity['entity_id']}','moisture_status') == 'ok' else 'water-off' }}}}")
    print(f"      x: 2")
    print(f"      y: { y }")
    print(f"      size: 20")
    print(f"      fill: >-")
    print(f"        {{{{ 'black' if state_attr('{plant_entity['entity_id']}','moisture_status') == 'ok' else 'red' }}}}")
    print(f"      anchor: ls")

    # Conductivity
    print(f"    - type: icon")
    print(f"      value: >-")
    print(f"        {{{{ 'leaf' if state_attr('{plant_entity['entity_id']}','conductivity_status') == 'ok' else 'leaf-off' }}}}")
    print(f"      x: 20")
    print(f"      y: { y }")
    print(f"      size: 20")
    print(f"      fill: >-")
    print(f"       {{{{ 'black' if state_attr('{plant_entity['entity_id']}','conductivity_status') == 'ok' else 'red' }}}}")
    print(f"      anchor: ls")

    # Values
    print(f"    - type: text")
    print(f"      value: >-")
    print(f"        {{{{ state_attr('{plant_entity['entity_id']}','friendly_name') }}}} ({{{{ states('sensor.{sensor_name}_soil_moisture') | int(0) }}}}%/{{{{states('sensor.{sensor_name}_conductivity') | int(0) }}}})")
    print(f"      font: rcm.ttf")
    print(f"      x: 46")
    print(f"      y: { y }")
    print(f"      size: 14")
    print(f"      color: black")
    print(f"      anchor: lb")


async def main() -> None:
    """
    Main function for the script.
    Establishes a connection with the Home Assistant WebSocket API,
    retrieves plant entities grouped by their area, and outputs formatted YAML for each plant.

    Workflow:
        1. Connects to the Home Assistant WebSocket API using credentials from my_secrets.
        2. Retrieves plant information grouped by area using `get_plants_sorted_on_area`.
        3. Outputs Esphome YAML configuration for each plant, grouped by its area.

    Args:
        None

    Returns:
        None
    """
    client = HomeAssistantWebSocketClient(my_secrets.HA_HOST, my_secrets.HA_PORT, my_secrets.HA_TOKEN)
    await client.connect()

    # Get plants, sorted on Area
    plants = await client.get_plants_sorted_on_area()

    for key in plants.keys():
        output_template_header(plants[key])
        for i, plant_entity in enumerate(plants[key]):
            output_mushroom_template(plant_entity, i)


if __name__ == "__main__":
    """
    Entry point for the script. Runs the main async logic.
    """
    asyncio.run(main())