"""DataUpdateCoordinator for Ecowitt IoT."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)


class EcowittDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Ecowitt data."""

    config_entry: ConfigEntry

    def __init__(
        self, 
        hass: HomeAssistant, 
        session: aiohttp.ClientSession,
        host: str,
        devices: list[EcowittDeviceDescription]
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = host
        self.devices = devices
        self.session = session

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        try:
            async with async_timeout.timeout(10):
                return await self._fetch_data()
        except Exception as error:
            raise UpdateFailed(f"Error communicating with API: {error}")

    async def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        data = {}
        for device in self.devices:
            device_data = await self._fetch_device_data(device)
            if device_data:
                data[device.device_id] = device_data
        return data

    async def _fetch_device_data(self, device: EcowittDeviceDescription) -> dict[str, Any]:
        """Fetch data for a specific device."""
        url = f"http://{self.host}/parse_quick_cmd_iot"
        payload = {
            "command": [{
                "cmd": "read_device",
                "id": device.device_id,
                "model": device.model
            }]
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                text = await response.text()
                # Clean the response
                text = text.strip(' %\n\r')
                
                try:
                    return json.loads(text)
                except json.JSONDecodeError as err:
                    _LOGGER.error(
                        "Error parsing JSON for device %s: %s. Response: %s",
                        device.device_id, err, text
                    )
                    raise
        except Exception as error:
            _LOGGER.error(
                "Error fetching data for device %s: %s", device.device_id, error
            )
            raise
