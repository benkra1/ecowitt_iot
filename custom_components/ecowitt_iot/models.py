"""Models for Ecowitt IoT integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MODEL_AC1100, MODEL_WFC01

MANUFACTURER: Final = "Ecowitt"


@dataclass
class EcowittDeviceDescription:
    """Representation of an Ecowitt device."""

    device_id: str
    model: int
    name: str | None = None
    sw_version: str | None = None

    @property
    def model_name(self) -> str:
        """Get the model name of the device."""
        return "WFC01" if self.model == MODEL_WFC01 else "AC1100"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=self.name or f"{self.model_name} {self.device_id}",
            manufacturer=MANUFACTURER,
            model=self.model_name,
            sw_version=self.sw_version,
        )