import asyncio
from typing import List, Dict, Any

import my_secrets
from home_assistant_websocket_client import HomeAssistantWebSocketClient

client = HomeAssistantWebSocketClient(my_secrets.HA_HOST, my_secrets.HA_PORT, my_secrets.HA_TOKEN)

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
    print(f"============================")
    print(f"{area_name}")
    print(f"============================")
    print(f"type: vertical-stack")
    print(f"cards:")

async def output_mushroom_template(plant_entity: Dict[str, Any]) -> None:
    """
    Outputs the detailed mushroom-template-card configuration for a plant entity.

    Args:
        plant_entity (Dict[str, Any]): A dictionary containing metadata for a single plant entity.
            It should include fields such as 'entity_id', 'name', and so on.

    Returns:
        None
    """
    entity_id: str = plant_entity['entity_id']
    sensor_name: str = entity_id.split('.')[1]
    moisture_sensor_name: str = 'sensor.' + sensor_name + '_soil_moisture'      
    print( "  - type: custom:mushroom-template-card")
    print(f"    entity: {plant_entity['entity_id']}")
    print(f"    primary: {plant_entity['name']}")
    print( "    picture: \"{{ state_attr(entity, 'entity_picture') }}\"")
    print(f"    secondary: >")

    # Basic plant, moisture
    print(f"      {{% set moisture = states('{moisture_sensor_name}') %}}")
    print( "      {% set moisture_ok = state_attr(entity, 'moisture_status') == 'ok' %}")
    print( "      {% if moisture_ok %} 💧{% else %} 🩸{% endif %} {{ moisture }}%")

    # MiFlora sensor
    conductivity_sensor_name: str = 'sensor.' + sensor_name + '_conductivity'
    if await client.entity_attr_exists(conductivity_sensor_name, "external_sensor"):
        conductivity_real_name = await client.get_state_attr(conductivity_sensor_name, 'external_sensor')
        battery_sensor_name = conductivity_real_name.replace('conductivity', 'battery')
        print(f"      {{% set conductivity = states('{conductivity_sensor_name}') %}}")
        print( "      {% set conductivity_ok = state_attr(entity, 'conductivity_status') == 'ok' %}")
        print(f"      {{% set battery = states('{battery_sensor_name}') %}}")
        print( "      {% set battery_ok = (battery | int > 15) if battery is not none and battery != 'unknown' else false %}")
        print( "      {% if conductivity_ok %} - 🌿{% else %} - 🌱{% endif %} {{ conductivity }} µS/cm")
        print( "      {% if battery_ok %} 🔋 {% else %} 🪫 {% endif %} {{ battery }}%")

    print( "      ({{ relative_time(states[entity].last_updated) }})")
    print( "    badge_icon: |")
    print( "      {% if is_state_attr(entity, 'moisture_status', 'ok') %} mdi:water {% else %} mdi:water-alert {% endif %}")
    print( "    badge_color: |")
    print( "      {% if is_state_attr(entity, 'moisture_status', 'ok') %} green {% else %} red {% endif %}")
    print( "    features_position: bottom")
    print( "    grid_options:")
    print( "      columns: 12")
    print( "      rows: 1")

async def main() -> None:
    """
    Main function for the script.
    Establishes a connection with the Home Assistant WebSocket API,
    retrieves plant entities grouped by their area, and outputs formatted YAML for each plant.

    Workflow:
        1. Connects to the Home Assistant WebSocket API using credentials from my_secrets.
        2. Retrieves plant information grouped by area using `get_plants_sorted_on_area`.
        3. Outputs Esphome YAML configuration for each plant, grouped by its area.

    Returns:
        None
    """
    await client.connect()

    # Get plants, sorted on Area
    plants = await client.get_plants_sorted_on_area()

    for key in plants.keys():
        # Sort plants in each area alphabetically by name before output
        sorted_plants = sorted(plants[key], key=lambda p: (p.get('name') or '').lower())
        output_template_header(sorted_plants)
        for plant_entity in sorted_plants:
            await output_mushroom_template(plant_entity)


if __name__ == "__main__":
    """
    Entry point for the script. Runs the main async logic.
    """
    asyncio.run(main())