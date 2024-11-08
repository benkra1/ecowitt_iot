"""Support for Ecowitt IoT switches."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODEL_AC1100
from .coordinator import EcowittDataUpdateCoordinator
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)


@dataclass
class EcowittSwitchEntityDescription(SwitchEntityDescription):
    """Describes Ecowitt switch entity."""

    status_key: str = ""


SWITCH_DESCRIPTIONS = {
    MODEL_AC1100: EcowittSwitchEntityDescription(
        key="power_switch",
        name="Power",
        status_key="ac_status",
    ),
    1: EcowittSwitchEntityDescription(  # WFC01
        key="valve_switch",
        name="Valve",
        status_key="water_status",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt switch based on a config entry."""
    coordinator: EcowittDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        EcowittSwitch(
            coordinator=coordinator,
            device=device,
            description=SWITCH_DESCRIPTIONS[device.model],
        )
        for device in coordinator.devices
        if device.model in SWITCH_DESCRIPTIONS
    )


class EcowittSwitch(CoordinatorEntity[EcowittDataUpdateCoordinator], SwitchEntity):
    """Representation of an Ecowitt switch."""

    entity_description: EcowittSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcowittDataUpdateCoordinator,
        device: EcowittDeviceDescription,
        description: EcowittSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device.device_id}_{description.key}"
        self._attr_device_info = device.device_info
        self._attr_name = description.name

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        try:
            device_data = self.coordinator.data[self._device.device_id]["command"][0]
            return bool(device_data.get(self.entity_description.status_key, 0))
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
        