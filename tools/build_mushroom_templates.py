import asyncio
from typing import List, Dict, Any

import my_secrets
from home_assistant_websocket_client import HomeAssistantWebSocketClient

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
    print(f"  - type: custom:mushroom-title-card")
    print(f"    title: {area_name}")

def output_mushroom_template(plant_entity: Dict[str, Any]) -> None:
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
    print( "  - type: custom:mushroom-template-card")
    print(f"    entity: {plant_entity['entity_id']}")
    print(f"    primary: {plant_entity['name']}")
    print( "    picture: \"{{ state_attr(entity, 'entity_picture') }}\"")
    print(f"    secondary: >")

    # Might want to do this lookup in this code
    print( "      {% set sensor_name = entity.split('.')[1] %}")
    print( "      {% set sensor = state_attr('sensor." + sensor_name + "_soil_moisture', 'external_sensor') %}")
    print( "      {% set battery = sensor.replace('moisture', 'battery') %}")

    print( "      {% if state_attr(entity, 'moisture_status') == 'ok'  %} 💧{% else %} 🩸{% endif %}")
    print( "      {{ states('sensor." + sensor_name + "_soil_moisture', with_unit=True) }} - ")
    print( "      {% if state_attr(entity, 'conductivity_status') == 'ok'  %} 🌿{% else %} 🌱{% endif %}")
    print( "      {{ states('sensor." + sensor_name + "_conductivity', with_unit=True) }}")
    print( "      {% if has_value(battery) %} - ")
    print( "      {% if states(battery) | int > 15 %} 🔋 {% else %} 🪫 {% endif %}")
    print( "      {{ states(battery, with_unit=True) }} {% endif %}")
    print( "      ({{ relative_time(states[entity].last_updated) }})")

    print( "    badge_icon: |")
    print( "      {% if is_state_attr(entity, 'moisture_status', 'ok') %} mdi:water {% else %} mdi:water-alert {% endif %}")
    print( "    badge_color: |")
    print( "      {% if is_state_attr(entity, 'moisture_status', 'ok') %} green {% else %} red {% endif %}")


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
        for plant_entity in plants[key]:
            output_mushroom_template(plant_entity)


if __name__ == "__main__":
    """
    Entry point for the script. Runs the main async logic.
    """
    asyncio.run(main())