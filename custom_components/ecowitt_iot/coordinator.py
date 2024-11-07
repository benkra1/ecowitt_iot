async def _fetch_device_data(self, device: EcowittDeviceDescription) -> dict[str, Any]:
        """Fetch data for a specific device."""
        url = f"http://{self.host}/parse_quick_cmd_iot"
        payload = {
            "command": [{
                "cmd": "read_device",
                "id": device.device_id,
                "model": device.model
            }]
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                text = await response.text()
                # Clean the response
                text = text.strip(' %\n\r')
                
                try:
                    return json.loads(text)
                except json.JSONDecodeError as err:
                    _LOGGER.error(
                        "Error parsing JSON for device %s: %s. Response: %s",
                        device.device_id, err, text
                    )
                    raise
        except Exception as error:
            _LOGGER.error(
                "Error fetching data for device %s: %s", device.device_id, error
            )
            raise
