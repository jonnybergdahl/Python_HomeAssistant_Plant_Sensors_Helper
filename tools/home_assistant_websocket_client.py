import asyncio
import json
from collections import defaultdict

import websockets
from typing import Dict, List, Optional

from construct.lib import OrderedDict

from my_secrets import HA_HOST, HA_PORT, HA_TOKEN


class HomeAssistantWebSocketClient:
    def __init__(self, host, port, token):
        """
        Initialize the Home Assistant WebSocket Client.
        :param host: Hostname or IP address of the Home Assistant instance
        :param port: Port number of the Home Assistant WebSocket API
        :param token: Long-lived access token for authentication
        """
        self.host = host
        self.port = port
        self.token = token

        self.websocket = None
        self.message_id = 0

        self._areas = None
        self._plant_devices = None

    async def connect(self):
        """
        Connect to the Home Assistant WebSocket API.
        """
        uri = f"ws://{self.host}:{self.port}/api/websocket"
        self.websocket = await websockets.connect(uri, max_size = 100 * 1024 * 1024)
        # Set up authentication
        response = await self.websocket.recv()
        response_json = json.loads(response)
        if response_json.get("type") == "auth_required":
            await self.websocket.send(json.dumps({"type": "auth", "access_token": self.token}))
            auth_response = json.loads(await self.websocket.recv())
            if auth_response.get("type") != "auth_ok":
                raise Exception("Authentication failed: " + str(auth_response))
        print("Connected and authenticated to Home Assistant WebSocket API.")
        self._areas = await self.get_areas()
        self._plant_devices = await self.get_plant_device_dict()


    async def _send_message(self, message_type, payload=None):
        """
        Send a message to the WebSocket API.
        :param message_type: Type of message to send
        :param payload: Additional plant_entity for the message
        :return: API response
        """
        if self.websocket is None:
            raise Exception("WebSocket connection is not established.")

        self.message_id += 1
        message = {
            "id": self.message_id,
            "type": message_type,
        }
        if payload:
            message.update(payload)
        await self.websocket.send(json.dumps(message))

        response = await self.websocket.recv()
        return json.loads(response)

    async def get_areas(self) -> Dict[str, str]:
        """
        Sends a request to the area registry to retrieve a list of configured areas and returns them as a dictionary.

        :return: A dictionary where keys are area IDs and values are area names.
        """
        response = await self._send_message("config/area_registry/list")
        result = response.get("result", [])
        areas = { area["area_id"]: area["name"] for area in result }
        return areas

    async def get_plant_devices(self) -> List[Dict[str, Optional[str]]]:
        devices =  await self.get_plant_device_dict()
        plant_result = []
        for device in devices:
            device_id = device.get("id")
            area_id = device.get("area_id")
            if area_id in self._areas:
                area_name = self._areas[area_id]
            else:
                area_name = None
            name = device["name"]
            model = device["model"]

            plant_result.append({
                "device_id": device_id,
                "area_id": area_id,
                "area_name": area_name,
                "name": name,
                "model": model,
            })

        # Sort plant_result by the "name" key
        sorted_result = sorted(plant_result, key=lambda x: x["name"].lower())
        return sorted_result

    async def get_plants_sorted_on_area(self):
        plants = await self.get_plant_entities()

        result = defaultdict(list)
        for plant in plants:
            result[plant["area_name"]].append(plant)
        sorted_result = OrderedDict(sorted(result.items()))
        return sorted_result

    async def get_entity_config(self, entity_id: str):
        response = await self._send_message("config/entity_registry/list")
        config = response.get("result", [])
        match = [item for item in config if item["entity_id"] == entity_id]
        if not match:
            return None

        return match[0]

    async def get_state(self, entity_id: str):
        response = await self._send_message("get_states")
        states = response.get("result", [])
        match = [item for item in states if item["entity_id"] == entity_id]
        if not match:
            return None

        return match[0]

    async def get_plant_device_dict(self):
        """
        Retrieve the list of devices in Home Assistant.
        :return: List of devices
        """
        response = await self._send_message("config/device_registry/list")
        result = response.get("result", [])

        domain_result = {}
        for device in result:
            if any(identifier[0] == "plant" for identifier in device.get("identifiers", [])):
                device_id = device.get("id")
                domain_result[device_id] = device
        return domain_result

    async def get_plant_entities(self):
        response = await self._send_message("config/entity_registry/list")
        result = response.get("result", [])

        domain_result = []
        for entity in result:
            if str(entity.get("entity_id")).startswith("plant"):
                entity_id = str(entity.get("entity_id"))
                device_id = entity.get("device_id")
                area_id = self._plant_devices[device_id]["area_id"]
                if area_id in self._areas:
                    area_name = self._areas[area_id]
                else:
                    area_name = None
                name = entity["name"]
                # Now get name of underlying sensor
                moisture_entity = entity_id.replace("plant.", "sensor.") + "_soil_moisture"
                # Extract external_sensor
                state = await self.get_state(moisture_entity)
                external_sensor = state
                crap = await self.get_entity_config(moisture_entity)

                if name is None:
                    name = entity.get("original_name")
                domain_result.append({
                    "entity_id": entity_id,
                    "device_id": device_id,
                    "area_id": area_id,
                    "area_name": area_name,
                    "name": name,
                    "moisture_entity": moisture_entity,
                })
        return domain_result

    async def get_plant_states(self):
        response = await self._send_message("get_states")
        result = response.get("result", [])

        domain_result = []
        for entity in result:
            if str(entity.get("entity_id")).startswith("plant"):
                domain_result.append(entity)
        return domain_result

    async def entity_exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists in Home Assistant.
        
        Args:
            entity_id: The entity ID to check
            
        Returns:
            bool: True if entity exists, False otherwise
        """
        response = await self._send_message("get_states")
        states = response.get("result", [])
        return any(item["entity_id"] == entity_id for item in states)

    async def entity_attr_exists(self, entity_id: str, attr: str) -> bool:
        """
        Check if an attribute exists for an entity in Home Assistant.
        
        Args:
            entity_id: The entity ID to check
            attr: The attribute name to check
            
        Returns:
            bool: True if attribute exists, False otherwise
        """
        state = await self.get_state(entity_id)
        if not state:
            return False

        return attr in state.get("attributes", {})

    async def get_state_attr(self, entity_id: str, attr: str):
        """
        Get a specific attribute from an entity's state.
    
        Args:
            entity_id: The entity ID to get the attribute from
            attr: The name of the attribute to retrieve
    
        Returns:
            The attribute value if found, None otherwise
        """
        state = await self.get_state(entity_id)
        if not state:
            return None

        return state.get("attributes", {}).get(attr)

    async def call_service(self, domain, service, service_data):
        """
        Call a service in Home Assistant, e.g., turning on a light.
        :param domain: The integration domain (e.g., 'light')
        :param service: The specific service to call (e.g., 'turn_on')
        :param service_data: The service plant_entity (e.g., {"entity_id": "light.living_room"})
        :return: API response
        """
        payload = {
            "domain": domain,
            "service": service,
            "service_data": service_data,
        }
        return await self._send_message("call_service", payload)

    async def close(self):
        """
        Close the WebSocket connection.
        """
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            print("WebSocket connection closed.")

# Example usage
if __name__ == "__main__":
    async def main():

        client = HomeAssistantWebSocketClient(HA_HOST, HA_PORT, HA_TOKEN)
        await client.connect()

        # Get plant
        plants = await client.get_plants_sorted_on_area()

        for key in plants.keys():
            print(key)
            for plant in plants[key]:
                print(json.dumps(plant))

        await client.close()

    asyncio.run(main())


