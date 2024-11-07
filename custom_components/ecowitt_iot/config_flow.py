"""Config flow for Ecowitt IoT integration."""
from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, MODEL_AC1100, MODEL_WFC01, CONF_DEVICE_ID, CONF_MODEL

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(CONF_MODEL): vol.In(
            {
                "WFC01": MODEL_WFC01,
                "AC1100": MODEL_AC1100,
            }
        ),
    }
)

STEP_DEVICES_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("devices"): vol.All(
            cv.ensure_list,
            [DEVICE_SCHEMA],
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    async with session.get(
        f"http://{data[CONF_HOST]}/get_iot_device_list",
        timeout=10,
    ) as response:
        response.raise_for_status()
        await response.json()


class EcowittConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ecowitt IoT."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except asyncio.TimeoutError:
                errors["base"] = "timeout_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
            else:
                self._host = user_input[CONF_HOST]
                return await self.async_step_devices()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"Ecowitt IoT ({self._host})",
                data={
                    CONF_HOST: self._host,
                    "devices": user_input["devices"],
                },
            )

        return self.async_show_form(
            step_id="devices",
            data_schema=STEP_DEVICES_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle reauth if the device is unreachable."""
        return await self.async_step_user()
