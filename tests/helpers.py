from __future__ import annotations
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import async_get_current_platform

_LOGGER = logging.getLogger(__name__)


class MockEntityAdder:
    """Helper class to track added entities in tests."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the helper."""
        self.hass = hass
        self.entities: list[Entity] = []

    async def async_add_entities(self, entities: list[Entity]):
        """Track added entities and add them to Home Assistant."""
        self.entities.extend(entities)

        # Add entities to Home Assistant state machine
        for entity in entities:
            # Set Home Assistant instance
            entity.hass = self.hass

            try:
                # Add to HA state machine
                entity.entity_id = f"switch.{entity._device.name.lower().replace(' ', '_')}_valve"
                await entity.async_added_to_hass()

                # Generate initial state
                await entity.async_update_ha_state(force_refresh=True)

                _LOGGER.debug(
                    "Added entity %s with state %s", entity.entity_id, entity.state
                )

            except Exception as err:
                _LOGGER.error(
                    "Error adding entity %s: %s", entity.entity_id, err, exc_info=True
                )
                raise
