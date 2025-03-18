import paho.mqtt.client as mqtt
import json
import time
import datetime

BROKER = "localhost"
PORT = 1883
TOPICS = {
    "gps": "logix/gps",
    "temperature": "logix/temperature",
    "humidity": "logix/humidity",
}

def publish_message(client, topic, message):
    """Publica un mensaje en un topic específico."""
    try:
        client.publish(topic, json.dumps(message), qos=2)
        print(f"📤 Publicado en {topic}: {message}")
    except Exception as e:
        print(f"❌ Error al publicar en {topic}: {e}")

def connect_mqtt():
    """Crea y configura un cliente MQTT con reconexión."""
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.loop_start()  # Manejar conexión en segundo plano
    return client

client = connect_mqtt()

while True:
    try:
        # Simular datos GPS
        gps_data = {"lat": 19.4326, "lon": -99.1332, "speed": 60}
        publish_message(client, TOPICS["gps"], gps_data)

        # Simular temperatura
        temperature_data = {
            "temperature": 5.0,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        publish_message(client, TOPICS["temperature"], temperature_data)

        # Simular humedad
        humidity_data = {
            "humidity": 65,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        publish_message(client, TOPICS["humidity"], humidity_data)

        time.sleep(5)  # Publicar cada 5 segundos

    except Exception as e:
        print(f"⚠️ Error en el bucle principal: {e}")
        time.sleep(5)  # Esperar antes de intentar de nuevo
