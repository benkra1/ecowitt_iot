"""DataUpdateCoordinator for Ecowitt IoT."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)


class EcowittDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Ecowitt data."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, devices: list[EcowittDeviceDescription]
    ) -> None:
        """Initialize global Ecowitt data updater."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

        self.config_entry = entry
        self.devices = devices
        self._session = async_get_clientsession(hass)
        self._host = entry.data[CONF_HOST]

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                return await self._fetch_device_data()
        except asyncio.TimeoutError as error:
            raise UpdateFailed(f"Timeout communicating with API: {error}") from error
        except Exception as error:
            raise UpdateFailed(f"Error communicating with API: {error}") from error

    async def _fetch_device_data(self) -> dict[str, Any]:
        """Fetch data from devices."""
        device_data = {}
        for device in self.devices:
            try:
                async with self._session.post(
                    f"http://{self._host}/parse_quick_cmd_iot",
                    json={
                        "command": [{
                            "cmd": "read_device",
                            "id": device.device_id,
                            "model": device.model
                        }]
                    }
                ) as resp:
                    if resp.status == 200:
                        device_data[device.device_id] = await resp.json()
            except Exception as error:
                _LOGGER.error(
                    "Error fetching data for device %s: %s", device.device_id, error
                )

        return device_data
