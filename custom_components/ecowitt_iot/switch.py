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

    status_key: str | None = None
    cmd_on: str = "quick_run"
    cmd_off: str = "quick_stop"


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

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        try:
            device_data = self.coordinator.data[self._device.device_id]["command"][0]
            return bool(device_data.get(self.entity_description.status_key, 0))
        except (KeyError, IndexError):
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        payload = {
            "command": [{
                "cmd": self.entity_description.cmd_on,
                "on_type": 0,
                "off_type": 0,
                "always_on": 1,
                "on_time": 0,
                "off_time": 0,
                "val_type": 0,
                "val": 0,
                "id": self._device.device_id,
                "model": self._device.model,
            }]
        }

        await self._send_command(payload)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        payload = {
            "command": [{
                "cmd": self.entity_description.cmd_off,
                "id": self._device.device_id,
                "model": self._device.model,
            }]
        }

        await self._send_command(payload)

    async def _send_command(self, payload: dict[str, Any]) -> None:
        """Send command to device."""
        session = self.coordinator.session
        url = f"http://{self.coordinator._host}/parse_quick_cmd_iot"

        try:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                await response.json()
        except Exception as error:
            _LOGGER.error("Error sending command to %s: %s", self._device.device_id, error)
            raise
        finally:
            await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self._device.device_id in self.coordinator.data
            and len(self.coordinator.data[self._device.device_id].get("command", [])) > 0
        )
