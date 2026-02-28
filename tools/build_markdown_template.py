"""
build_markdown_template.py

This script generates a single markdown template for Home Assistant dashboards
that uses internal Home Assistant functions to enumerate and display plant entities.
The template groups plants by area and displays their moisture levels and status.
"""

def main() -> None:
    """
    Main function for the script.
    Outputs a single markdown template that uses Home Assistant's internal functions
    to enumerate plant entities, group them by area, and display their status.
    
    The template uses Home Assistant's templating system to:
    1. Get all plant entities
    2. Group them by area
    3. Display moisture levels, status, and additional details for each plant
    
    Args:
        None
        
    Returns:
        None
    """
    # Output the template header
    print("type: markdown")
    print("content: |")
    print("  {% set plant_entities = states | selectattr('entity_id', 'match', '^plant\\.') | selectattr('attributes.device_class', 'eq', 'plant') | list %}")
    print("  {% if plant_entities | count > 0 %}")
    
    # Group plants by area
    print("  {% set areas = namespace(list=[]) %}")
    print("  {% for entity in plant_entities %}")
    print("    {% set dev_id = device_id(entity.entity_id) %}")
    print("    {% set ar_id = area_id(dev_id) %}")
    print("    {% set cur_area = area_name(ar_id) if ar_id else 'Unknown Area' %}")
    print("    {% if cur_area not in areas.list %}")
    print("      {% set areas.list = areas.list + [cur_area] %}")
    print("    {% endif %}")
    print("  {% endfor %}")
    
    # Sort areas alphabetically
    print("  {% set sorted_areas = areas.list | sort %}")
    
    # For each area, display plants
    print("  {% for area in sorted_areas %}")
    print("  ## 🪴 {{ area }}")
    print("  <table style=\"width:100%; border-collapse: collapse; margin-bottom: 10px;\">")
    print("  <tr>")
    print("  <th style=\"text-align: left; padding: 8px; border: 1px solid;\">Plant</th>")
    print("  <th style=\"text-align: left; padding: 8px; border: 1px solid;\">Moisture</th>")
    print("  <th style=\"text-align: left; padding: 8px; border: 1px solid;\">Conductivity</th>")
    print("  <th style=\"text-align: left; padding: 8px; border: 1px solid;\">Battery</th>")
    print("  </tr>")
    
    # Filter plants for current area and display them
    print("  {% for entity in plant_entities %}")
    print("    {% set dev_id = device_id(entity.entity_id) %}")
    print("    {% set ar_id = area_id(dev_id) %}")
    print("    {% set current_area = area_name(ar_id) if ar_id else 'Unknown Area' %}")
    print("    {% if current_area == area %}")
    print("      {% set sensor_name = entity.entity_id.split('.')[1] %}")
    print("      {% set moisture_sensor = 'sensor.' + sensor_name + '_soil_moisture' %}")
    print("      {% set conductivity_sensor = 'sensor.' + sensor_name + '_conductivity' %}")
    print("      {% set miflora_sensor = state_attr(conductivity_sensor, 'external_sensor') %}")
    print("  <tr>")
    print("  <td style=\"padding: 8px; border: 1px solid;\"><strong>{{ entity.name }}</strong></td>")
    print("  <td style=\"padding: 8px; border: 1px solid;\">{{ '✅' if is_state_attr(entity.entity_id, 'moisture_status', 'ok') else '❌' }} {{ states(moisture_sensor) }}%</td>")
    # Check if it has a conductivity sensor
    print("      {% if states(conductivity_sensor) != 'unknown'%}")
    print("  <td style=\"padding: 8px; border: 1px solid;\">{{ '✅' if is_state_attr(entity.entity_id, 'conductivity_status', 'ok') else '❌' }} {{ states(conductivity_sensor) }}</td>")
    # Check if it's a MiFlora sensor
    print("      {% else %}")
    print("  <td></td>")
    print("      {% endif %}")      # if conductivity
    print("      {% if miflora_sensor %}")
    print("         {% set battery_sensor = miflora_sensor.replace('_conductivity', '_battery') %}")
    print("  <td style=\"padding: 8px; border: 1px solid;\">{{ '✅' if states(battery_sensor) | int(default=0) > 10 else '❌' }} {{ states(battery_sensor) }}%</td>")
    print("        {% else %}")
    print("  <td></td>")
    print("        {% endif %}")    # if mi_flora
    print("  </tr>")
    print("    {% endif %}")
    print("  {% endfor %}")
    print("  </table>")
    # Add separator between areas
    print("  {% if not loop.last %}")
    print("  <hr style=\"margin: 20px 0;\">")
    print("  {% endif %}")
    print("  {% endfor %}")
    
    # Handle case when no plant entities are found
    print("  {% else %}")
    print("  No plant entities found.")
    print("  {% endif %}")

if __name__ == "__main__":
    """
    Entry point for the script.
    """
    main()