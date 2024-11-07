"""The Ecowitt IoT integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_DEVICE_ID, CONF_MODEL, DOMAIN
from .coordinator import EcowittDataUpdateCoordinator
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ecowitt IoT from a config entry."""
    try:
        devices = [
            EcowittDeviceDescription(
                device_id=device[CONF_DEVICE_ID],
                model=device[CONF_MODEL],
            )
            for device in entry.data.get("devices", [])
        ]

        coordinator = EcowittDataUpdateCoordinator(
            hass=hass,
            entry=entry,
            devices=devices,
        )

        await coordinator.async_config_entry_first_refresh()
    except asyncio.TimeoutError as ex:
        raise ConfigEntryNotReady(
            f"Timeout connecting to Ecowitt device at {entry.data[CONF_HOST]}"
        ) from ex
    except Exception as ex:
        raise ConfigEntryNotReady(
            f"Failed to connect to Ecowitt device at {entry.data[CONF_HOST]}: {str(ex)}"
        ) from ex

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        # Migration not implemented yet
        pass

    return True
