#!/usr/bin/env python3

import json
import logging

import paho.mqtt.client as mqtt

from telemetry.utils import get_mqtt_config

_LOGGER = logging.getLogger(__name__)

(
    B4MAD_RACING_MQTT_HOST,
    B4MAD_RACING_MQTT_PORT,
    B4MAD_RACING_MQTT_USER,
    B4MAD_RACING_MQTT_PASSWORD,
) = get_mqtt_config()

PAYLOAD_KEYS = [
    "Clutch",
    "Brake",
    "Throttle",
    "Handbrake",
    "SteeringAngle",
    "Rpms",
    "Gear",
    "SpeedMs",
    "DistanceRoundTrack",
    "WorldPosition_x",
    "WorldPosition_y",
    "WorldPosition_z",
    "CurrentLap",
    "CurrentLapTime",
    "LapTimePrevious",
    "CurrentLapIsValid",
    "PreviousLapWasValid",
    "CarClass",
]


def telemetry_from_dict(data: dict):
    payload = dict()
    for key in PAYLOAD_KEYS:
        if key in data:
            payload[key] = data[key]
    return payload


class Mqtt:
    def __init__(self):
        mqttc = mqtt.Client()
        mqttc.username_pw_set(B4MAD_RACING_MQTT_USER, B4MAD_RACING_MQTT_PASSWORD)
        self.client = mqttc

    def connect(self):
        self.client.connect(B4MAD_RACING_MQTT_HOST, B4MAD_RACING_MQTT_PORT)

    def disconnect(self):
        self.client.disconnect()

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload=payload, qos=0, retain=False)


class MqttPublisher:
    def __init__(self):
        self.mqtt = Mqtt()
        self.mqtt.connect()

    def publish_dict(self, topic: str, data: dict):
        # dict {time: int, telemetry: dict}
        data_str = json.dumps(data)
        self.mqtt.publish(topic, data_str)

    def publish_df_dict(self, data: dict):
        time = data.pop("_time")
        time = int(time.timestamp() * 1000.0)

        payload = {"time": time, "telemetry": telemetry_from_dict(data)}
        topic = data["topic"]
        self.publish_dict(topic, payload)
