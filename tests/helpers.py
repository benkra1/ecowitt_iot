"""Test helpers."""

from typing import Any, Callable, List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity


class MockEntityAdder:
    """Mock add entities helper that actually adds entities to hass."""

    def __init__(self, hass: HomeAssistant):
        """Initialize."""
        self.hass = hass
        self.entities: list[Entity] = []

    async def async_add_entities(
        self, entities: list[Entity], update_before_add: bool = True
    ) -> None:
        """Mock add entities."""
        for entity in entities:
            self.entities.append(entity)
            entity.hass = self.hass
            if hasattr(entity, "async_add_to_hass"):
                await entity.async_add_to_hass()
            if update_before_add and hasattr(entity, "async_update"):
                await entity.async_update()
            if hasattr(entity, "async_write_ha_state"):
                await entity.async_write_ha_state()
