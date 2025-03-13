import paho.mqtt.client as mqtt
import time
import json

BROKER = "localhost"
PORT = 1883

TOPIC_GPS = "logix/gps"
TOPIC_TEMPERATURA = "logix/temperatura"
TOPIC_HUMEDAD = "logix/humedad"
TOPIC_ESTADO = "logix/estado"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

while True:
    # Publicar datos GPS
    msg_gps = json.dumps({"lat": 19.4326, "lon": -99.1332, "speed": 60})
    client.publish(TOPIC_GPS, msg_gps)
    print(f"Publicado GPS: {msg_gps}")

    # Publicar temperatura
    msg_temperatura = json.dumps({"valor": 25, "unidad": "C"})
    client.publish(TOPIC_TEMPERATURA, msg_temperatura)
    print(f"Publicado Temperatura: {msg_temperatura}")

    # Publicar humedad
    msg_humedad = json.dumps({"valor": 80, "unidad": "%"})
    client.publish(TOPIC_HUMEDAD, msg_humedad)
    print(f"Publicado Humedad: {msg_humedad}")

    
    
    time.sleep(5)  # Publicar cada 5 segundos
