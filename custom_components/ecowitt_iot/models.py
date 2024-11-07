"""Models for Ecowitt IoT devices."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, MODEL_AC1100, MODEL_WFC01


@dataclass
class EcowittDeviceDescription:
    """Device description for Ecowitt IoT devices."""

    device_id: str
    model: int
    name: Optional[str] = None

    @property
    def model_name(self) -> str:
        """Get the model name of the device."""
        return "WFC01" if self.model == MODEL_WFC01 else "AC1100"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=self.name or f"{self.model_name} {self.device_id}",
            manufacturer="Ecowitt",
            model=self.model_name,
        )
