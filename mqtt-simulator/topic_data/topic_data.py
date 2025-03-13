import json
import paho.mqtt.client as mqtt
import time
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TopicData:
    """Clase base para la estructura de datos de los topics MQTT."""

    @staticmethod
    def gps(lat, lon, speed):
        return json.dumps({"lat": lat, "lon": lon, "speed": speed})

    @staticmethod
    def temperatura(valor):
        return json.dumps({"valor": valor, "unidad": "C"})

    @staticmethod
    def humedad(valor):
        return json.dumps({"valor": valor, "unidad": "%"})
