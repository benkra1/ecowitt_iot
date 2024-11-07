"""Config flow for Ecowitt IoT integration."""
from __future__ import annotations

import asyncio
import json
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

class ConfigFlowError(Exception):
    """Base class for config flow errors."""


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    
    try:
        _LOGGER.debug("Getting device list from %s", data[CONF_HOST])
        async with session.get(
            f"http://{data[CONF_HOST]}/get_iot_device_list",
            timeout=10,
        ) as response:
            _LOGGER.debug("Response status: %s", response.status)
            text = await response.text()
            
            # Clean the response - remove trailing % if present
            text = text.strip(' %\n\r')
            
            _LOGGER.debug("Cleaned response text: %s", text)
            
            try:
                devices = json.loads(text)
            except json.JSONDecodeError as err:
                _LOGGER.error("Failed to parse JSON: %s. Raw text: %s", err, text)
                raise ConfigFlowError("Invalid JSON response") from err
            
            if not isinstance(devices, dict) or "command" not in devices:
                raise ConfigFlowError("Invalid device list format")
            
            # Log discovered devices
            _LOGGER.info("Found devices: %s", devices["command"])
            return devices["command"]

    except asyncio.TimeoutError as err:
        _LOGGER.error("Timeout connecting to %s: %s", data[CONF_HOST], err)
        raise
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to %s: %s", data[CONF_HOST], err)
        raise


class EcowittConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ecowitt IoT."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._devices: list[dict[str, Any]] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                self._devices = await validate_input(self.hass, user_input)
                self._host = user_input[CONF_HOST]
                
                # If no devices found, show error
                if not self._devices:
                    _LOGGER.warning("No devices found")
                    errors["base"] = "no_devices"
                else:
                    _LOGGER.info("Found devices: %s", self._devices)
                    # Automatically create entry with discovered devices
                    devices_config = [
                        {
                            "id": str(device["id"]),
                            "model": device["model"]
                        }
                        for device in self._devices
                        if "id" in device and "model" in device
                    ]
                    
                    return self.async_create_entry(
                        title=f"Ecowitt IoT ({self._host})",
                        data={
                            CONF_HOST: self._host,
                            "devices": devices_config
                        },
                    )

            except asyncio.TimeoutError:
                errors["base"] = "timeout_connect"
            except (aiohttp.ClientError, Exception) as error:
                _LOGGER.exception("Connection error: %s", error)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )