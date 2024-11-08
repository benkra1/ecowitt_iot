"""The Ecowitt IoT integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import EcowittDataUpdateCoordinator
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ecowitt IoT from a config entry."""
    try:
        # Log the entry data to debug
        _LOGGER.debug("Setting up entry with data: %s", entry.data)
        
        devices_data = entry.data.get("devices", [])
        if not devices_data:
            _LOGGER.error("No devices found in config entry")
            raise ConfigEntryNotReady("No devices configured")

        devices = []
        for device_data in devices_data:
            try:
                device = EcowittDeviceDescription(
                    device_id=str(device_data["id"]),
                    model=int(device_data["model"]),
                    name=device_data.get("nickname"),
                    sw_version=str(device_data.get("version", "unknown")),
                )
                devices.append(device)
            except KeyError as err:
                _LOGGER.error("Missing required field for device: %s", err)
                continue

        if not devices:
            raise ConfigEntryNotReady("No valid devices configured")

        coordinator = EcowittDataUpdateCoordinator(
            hass=hass,
            entry=entry,
            devices=devices,
        )

        await coordinator.async_config_entry_first_refresh()

    except asyncio.TimeoutError as ex:
        raise ConfigEntryNotReady(
            f"Timeout connecting to device at {entry.data[CONF_HOST]}"
        ) from ex
    except Exception as ex:
        _LOGGER.exception("Failed to setup integration")
        raise ConfigEntryNotReady(
            f"Failed to connect to device at {entry.data[CONF_HOST]}: {str(ex)}"
        ) from ex

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
