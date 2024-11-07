"""Support for Ecowitt IoT binary sensors."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ERROR_BITS_AC1100, ERROR_BITS_WFC01
from .coordinator import EcowittDataUpdateCoordinator
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)

WARNING_DEVICE_CLASSES: Final = {
    "leak": BinarySensorDeviceClass.MOISTURE,
    "leak_current": BinarySensorDeviceClass.MOISTURE,
    "low_battery": BinarySensorDeviceClass.BATTERY,
    "temp_low": BinarySensorDeviceClass.TEMPERATURE,
    "temp_high": BinarySensorDeviceClass.TEMPERATURE,
    "offline": BinarySensorDeviceClass.CONNECTIVITY,
    "overload": BinarySensorDeviceClass.PROBLEM,
    "relay_abnormal": BinarySensorDeviceClass.PROBLEM,
    "no_water": BinarySensorDeviceClass.PROBLEM,
    "no_load": BinarySensorDeviceClass.PROBLEM,
    "low_current": BinarySensorDeviceClass.PROBLEM,
}


@dataclass
class EcowittBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Ecowitt binary sensor entity."""

    bit_position: int = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt binary sensors based on a config entry."""
    coordinator: EcowittDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[EcowittBinarySensor] = []

    for device in coordinator.devices:
        error_bits = ERROR_BITS_AC1100 if device.model == 2 else ERROR_BITS_WFC01
        for bit, warning_type in error_bits.items():
            entities.append(
                EcowittBinarySensor(
                    coordinator=coordinator,
                    device=device,
                    description=EcowittBinarySensorEntityDescription(
                        key=f"{warning_type}_{device.device_id}",
                        name=f"{device.model_name} {warning_type.replace('_', ' ').title()}",
                        device_class=WARNING_DEVICE_CLASSES.get(warning_type),
                        entity_category=EntityCategory.DIAGNOSTIC,
                        bit_position=bit,
                    ),
                )
            )

    async_add_entities(entities)


class EcowittBinarySensor(CoordinatorEntity[EcowittDataUpdateCoordinator], BinarySensorEntity):
    """Binary sensor for Ecowitt device warnings."""

    entity_description: EcowittBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcowittDataUpdateCoordinator,
        device: EcowittDeviceDescription,
        description: EcowittBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device = device

        self._attr_unique_id = f"{DOMAIN}_{device.device_id}_{description.key}"
        self._attr_device_info = device.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if warning is active."""
        try:
            device_data = self.coordinator.data[self._device.device_id]["command"][0]
            warning_byte = device_data.get("warning", 0)
            return bool(warning_byte & (1 << self.entity_description.bit_position))
        except (KeyError, IndexError):
            return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self._device.device_id in self.coordinator.data
            and len(self.coordinator.data[self._device.device_id].get("command", [])) > 0
        )
