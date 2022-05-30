"""Flask+Prometheus Paho MQTT Subsciber Script
Date created: 25 Dec 2021

Purpose:
  - Reading data from MQTT broker
  - Display data at /metrics endpoint with Prometheus
"""

# Import packages --------------------------------------------------------------
import paho.mqtt.client as mqtt
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest
import time


# Import vault -----------------------------------------------------------------
try:
    from vault import vault
except ImportError:
    print("Vault containing secrets not found, aborting...")
    raise


# Variables --------------------------------------------------------------------
content_type = str('text/plain; version=0.0.4; charset=utf-8')
topics = vault["topics"]
s_keys = vault["s_keys"]

# Dictionary of sensor reading, initialized with 0 -----------------------------
sensor_reading = {s: 0 for s in s_keys}


# Configure connection ---------------------------------------------------------
def connect_mqtt():
    """Connecting to MQTT broker
    Uses data imported from vault for connection
    """
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            # print("Connected to broker!")
            pass
        else:
            print("Connection failure with error code %d\n", rc)

    # Set client credentials
    client = mqtt.Client()
    client.username_pw_set(vault["user"], vault["password"])
    client.on_connect = on_connect
    client.connect(host=vault["host"], port=vault["port"])

    # Return
    return client


# Define subscribe function ----------------------------------------------------
def subscribe(client: mqtt, topic, s_key, msg_out=False):
    """Subscribing to topic and reading the message

    The on_message sub-function is a callback when subscriber client receives message
    After subscribing:
      - Loop is start with .loop_start() to fetch data
      - After receiving message, loop is closed with .loop_stop()

    Without closing it, Paho will eventually quits with "[errno 24] Too many open files"
    """
    def on_message(client, userdata, msg):
        sensor_reading[s_key] = msg.payload.decode()
        if msg_out:
            print(f"{s_key}: {sensor_reading[s_key]}")
        client.loop_stop()  # Stop client after receiving payload

    client.subscribe(topic)
    client.loop_start()     # Start the client
    client.on_message = on_message


# [Looping, for terminal] Inserting data into sensor_reading -------------------
def data_insert_looping():
    """Useful when debugging Paho.
    Prints data to the terminal.
    """
    while True:
        for t, s in zip(topics, s_keys):
            client = connect_mqtt()
            subscribe(client, topic=t, s_key=s)
            print(f"{s}: {sensor_reading[s]}")
            time.sleep(3)


# [For Flask] Inserting data into sensor_reading
def data_insert():
    for t, s in zip(topics, s_keys):
        client = connect_mqtt()
        subscribe(client, topic=t, s_key=s)


# Defining a Flask app ---------------------------------------------------------
app = Flask(__name__)


# Define metric names for Prometheus -------------------------------------------
current_temp = Gauge(
    "current_temperature",
    "the current temperature in degree celcius",
    ["room"]
)

current_humidity = Gauge(
    "current_humidity",
    "the current humidity as percentage",
    ["room"]
)


# Configure /metrics route on Flask --------------------------------------------
@app.route("/metrics")
def metrics():
    data_insert()
    current_temp.labels("home").set(sensor_reading["temp"])
    current_humidity.labels("home").set(sensor_reading["humidity"])
    return Response(generate_latest(), mimetype=content_type)


# Run the program --------------------------------------------------------------
if __name__ == "__main__":
    # data_insert_looping()
    app.run(host="0.0.0.0", port=5000)
