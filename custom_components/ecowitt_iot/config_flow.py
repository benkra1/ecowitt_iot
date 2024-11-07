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
                raise aiohttp.ClientError("Invalid JSON response") from err
            
            if not isinstance(devices, dict) or "command" not in devices:
                raise ValueError("Invalid device list format")
            
            # Log discovered devices
            _LOGGER.info("Found devices: %s", devices["command"])
            return devices["command"]

    except asyncio.TimeoutError as err:
        _LOGGER.error("Timeout connecting to %s: %s", data[CONF_HOST], err)
        raise
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to %s: %s", data[CONF_HOST], err)
        raise