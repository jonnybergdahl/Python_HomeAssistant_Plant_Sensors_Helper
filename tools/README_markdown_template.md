# HTML Table Template for Plant Sensors

## Overview

The `build_markdown_template.py` script generates a template with HTML tables for Home Assistant dashboards that displays plant sensor information. This template uses Home Assistant's internal functions to:

1. Enumerate all plant entities
2. Group them by area
3. Display their moisture levels, status, and additional details

## Changes from Previous Version

The previous version of the script used the `HomeAssistantWebSocketClient` to retrieve plant data and pre-generate the content. The new version:

- No longer uses the WebSocket client
- Creates a single template that uses Home Assistant's internal templating system
- Performs all plant enumeration and data processing within the template itself
- Groups plants by area dynamically using Home Assistant's area functions
- Uses HTML tables instead of markdown tables for better compatibility with Home Assistant dashboards
- Uses simplified HTML styling without color codes to avoid Jinja templating issues

## How to Use

1. Run the script to generate the template:
   ```
   python3 build_markdown_template.py > plant_template.yaml
   ```

2. Copy the contents of `plant_template.yaml` into your Home Assistant dashboard configuration.

3. Add the template to your dashboard as a markdown card.

## Template Features

The template provides:

- A list of all plants grouped by area
- Moisture level for each plant with percentage
- Status indicator (✅/❌) based on moisture status
- Additional details for MiFlora sensors (conductivity and battery levels)
- Proper handling of areas and sorting

## Important Notes

### Indentation

Proper indentation of HTML elements within Jinja2 control structures is critical for correct rendering. The template ensures that all HTML table rows (`<tr>`) and cells are properly indented within their respective `{% if %}` and `{% for %}` blocks. Improper indentation can cause rendering issues where table rows appear outside of the table structure.

## Home Assistant Functions Used

The template uses these Home Assistant functions:

- `states` with `selectattr` filters - To get all plant entities (filtering by entity ID pattern and device_class)
- `device_id()` - To get the device ID for an entity
- `area_id()` - To get the area ID for a device
- `area_name()` - To get the area name for an area ID
- `states()` - To get the state of sensors
- `is_state_attr()` - To check entity attributes
- `is_state()` - To check if sensors exist

## Example Output

When added to your Home Assistant dashboard, the template will display something like:

```
# 🪴 Plant Status

## 🪴 Plant Status: Living Room
<table style="width:100%; border-collapse: collapse; margin-bottom: 10px;">
  <tr>
    <th style="text-align: left; padding: 8px; border: 1px solid;">Plant</th>
    <th style="text-align: left; padding: 8px; border: 1px solid;">Moisture</th>
    <th style="text-align: left; padding: 8px; border: 1px solid;">Status</th>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid;"><strong>Monstera</strong></td>
    <td style="padding: 8px; border: 1px solid;">42%</td>
    <td style="padding: 8px; border: 1px solid;">✅</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid;"><em>↳ Details</em></td>
    <td style="padding: 8px; border: 1px solid;">Conductivity: 250 µS/cm</td>
    <td style="padding: 8px; border: 1px solid;">Battery: 89%</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid;"><strong>Snake Plant</strong></td>
    <td style="padding: 8px; border: 1px solid;">35%</td>
    <td style="padding: 8px; border: 1px solid;">✅</td>
  </tr>
</table>

<hr style="margin: 20px 0;">

## 🪴 Plant Status: Kitchen
<table style="width:100%; border-collapse: collapse; margin-bottom: 10px;">
  <tr>
    <th style="text-align: left; padding: 8px; border: 1px solid;">Plant</th>
    <th style="text-align: left; padding: 8px; border: 1px solid;">Moisture</th>
    <th style="text-align: left; padding: 8px; border: 1px solid;">Status</th>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid;"><strong>Basil</strong></td>
    <td style="padding: 8px; border: 1px solid;">28%</td>
    <td style="padding: 8px; border: 1px solid;">❌</td>
  </tr>
  <tr>
    <td style="padding: 8px; border: 1px solid;"><strong>Mint</strong></td>
    <td style="padding: 8px; border: 1px solid;">45%</td>
    <td style="padding: 8px; border: 1px solid;">✅</td>
  </tr>
</table>
```