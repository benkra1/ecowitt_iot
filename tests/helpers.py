"""Test helpers for Ecowitt IoT tests."""
from __future__ import annotations
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import async_get_current_platform

_LOGGER = logging.getLogger(__name__)

class MockEntityAdder:
    """Helper class to track added entities in tests."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the helper."""
        self.hass = hass
        self.entities: list[Entity] = []
        self.async_add_entities = self._async_add_entities

    async def _async_add_entities(self, entities: list[Entity], update_before_add=True):
        """Track added entities and add them to Home Assistant."""
        try:
            # Track the entities
            self.entities.extend(entities)

            # Add entities to Home Assistant state machine
            for entity in entities:
                # Set Home Assistant instance
                entity.hass = self.hass

                # Initialize the entity
                if update_before_add:
                    try:
                        if hasattr(entity, "coordinator"):
                            entity.coordinator.last_update_success = True
                        await entity.async_update()
                    except Exception as err:
                        _LOGGER.error("Error updating entity: %s", err)

                # Add to HA state machine
                try:
                    await entity.async_added_to_hass()
                except Exception as err:
                    _LOGGER.error("Error adding entity to HA: %s", err)

                # Generate initial state
                try:
                    await entity.async_update_ha_state(force_refresh=True)
                except Exception as err:
                    _LOGGER.error("Error updating entity state: %s", err)

            _LOGGER.debug(
                "Added %d entities: %s",
                len(entities),
                [entity.entity_id for entity in entities]
            )

        except Exception as err:
            _LOGGER.error("Error in async_add_entities: %s", err, exc_info=True)
            raise
