"""Config flow for Ecowitt IoT integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    
    try:
        _LOGGER.debug("Attempting to connect to %s", data[CONF_HOST])
        async with session.get(
            f"http://{data[CONF_HOST]}/get_iot_device_list",
            timeout=10,
        ) as response:
            _LOGGER.debug("Response status: %s", response.status)
            response.raise_for_status()
            result = await response.json()
            _LOGGER.debug("Response data: %s", result)
    except asyncio.TimeoutError as err:
        _LOGGER.error("Timeout connecting to %s: %s", data[CONF_HOST], err)
        raise
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to %s: %s", data[CONF_HOST], err)
        raise


class EcowittConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ecowitt IoT."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except asyncio.TimeoutError:
                _LOGGER.exception("Timeout error")
                errors["base"] = "timeout_connect"
            except (aiohttp.ClientError, Exception) as error:
                _LOGGER.exception("Connection error: %s", error)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Ecowitt IoT ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
