"""Support for Ecowitt IoT switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcowittDataUpdateCoordinator
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt switch based on a config entry."""
    coordinator: EcowittDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        EcowittSwitch(coordinator, device)
        for device in coordinator.devices
    ])


class EcowittSwitch(CoordinatorEntity[EcowittDataUpdateCoordinator], SwitchEntity):
    """Representation of an Ecowitt switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcowittDataUpdateCoordinator,
        device: EcowittDeviceDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device = device
        self._attr_name = f"{device.model_name} Switch"
        self._attr_unique_id = f"{DOMAIN}_{device.device_id}_switch"
        self._attr_device_info = device.device_info

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        try:
            device_data = self.coordinator.data[self._device.device_id]["command"][0]
            if self._device.model == 1:  # WFC01
                return bool(device_data.get("water_status", 0))
            else:  # AC1100
                return bool(device_data.get("ac_status", 0))
        except (KeyError, IndexError):
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.coordinator.set_device_state(self._device.device_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.coordinator.set_device_state(self._device.device_id, False)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self._device.device_id in self.coordinator.data
            and len(self.coordinator.data[self._device.device_id].get("command", [])) > 0
        )
        