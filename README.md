## fma-mqtt: Flask Mini App for MQTT to Prometheus

Reads MQTT data pushed from IoT device for topics specified inside `vault.py`.

## Vault

```python
vault = {
    "user": "mqtt_user",
    "password": "mqtt_password",
    "host": "localhost",
    "port": 1883,
    "topics": ["sensor/temp", "sensor/humidity"],
    "s_keys": ["temp", "humidity"]
}
```

Save this as `vault.py` inside the app root.

## Installing

```bash
# Start and activate virtualenv
python -m venv env
source env/bin/activate

# Install packages
pip install flask paho-mqtt prometheus_client

# Run
python3 app.py
```
