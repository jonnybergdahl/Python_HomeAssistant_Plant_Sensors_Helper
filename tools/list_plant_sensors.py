import asyncio
from typing import List, Dict, Any
from html import escape

import my_secrets
from home_assistant_websocket_client import HomeAssistantWebSocketClient

client = HomeAssistantWebSocketClient(my_secrets.HA_HOST, my_secrets.HA_PORT, my_secrets.HA_TOKEN)

async def print_plant_data(plant: Dict[str, Any]) -> str:
    """
    Bygger och returnerar en HTML-tabellrad med växtens data.

    Args:
        plant (Dict[str, Any]): Växtobjekt med nödvändig metadata.

    Returns:
        str: En HTML <tr>...</tr>-rad.
    """
    moisture_entity = plant['moisture_entity']
    moisture_device = await client.get_state_attr(moisture_entity, 'external_sensor')
    entity_id = escape(plant['entity_id'])
    name = escape(plant['name'])
    moisture_src = escape(str(moisture_device) if moisture_device is not None else "")
    return f"<tr><td>{entity_id}</td><td>{name}</td><td>{moisture_src}</td></tr>"

async def main() -> None:
    """
    Hämtar växtdata och genererar en HTML-fil med formaterad tabell.
    """
    await client.connect()

    # Hämta växter, grupperade per område
    plants = await client.get_plants_sorted_on_area()

    rows: List[str] = []
    for area_name, plant_list in plants.items():
        rows.append(f"<tr class='area-row'><th colspan='3'>{escape(area_name)}</th></tr>")
        for plant_entity in plant_list:
            row_html = await print_plant_data(plant_entity)
            rows.append(row_html)

    html_doc = f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Växtsensorer</title>
<style>
body {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; margin: 1rem; color: #222; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }}
thead th {{ background: #f5f5f5; text-align: left; }}
.area-row th {{ background: #e8f4ea; font-size: 1.05rem; text-align: left; }}
tbody tr:nth-child(even) td {{ background: #fafafa; }}
caption {{ caption-side: top; text-align: left; font-size: 1.25rem; margin-bottom: .5rem; font-weight: 600; }}
</style>
</head>
<body>
<table>
<caption>Växtsensorer</caption>
<thead>
<tr><th>Entity ID</th><th>Namn</th><th>Fuktgivare</th></tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>"""

    with open("plants.html", "w", encoding="utf-8") as f:
        f.write(html_doc)

if __name__ == "__main__":
    """
    Entry point för skriptet. Kör huvudlogiken (async).
    """
    asyncio.run(main())

