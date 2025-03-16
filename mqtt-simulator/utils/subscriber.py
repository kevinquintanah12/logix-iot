import paho.mqtt.client as mqtt
import json
import time

BROKER = "localhost"
PORT = 1883
TOPICS = ["logix/gps", "logix/temperature", "logix/humidity"]

def on_connect(client, userdata, flags, rc):
    """Maneja la conexión al broker."""
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        for topic in TOPICS:
            client.subscribe(topic, qos=2)
            print(f"📡 Suscrito a {topic} con QoS 2")
    else:
        print(f"⚠️ Error de conexión: {rc}")

def on_message(client, userdata, msg):
    """Maneja los mensajes recibidos."""
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📩 Mensaje recibido en {msg.topic}: {payload}")
    except json.JSONDecodeError:
        print(f"❌ Error al decodificar JSON en {msg.topic}")

def on_disconnect(client, userdata, rc):
    """Maneja la desconexión y reintento de conexión."""
    print("🔴 Desconectado del broker. Intentando reconectar en 5 segundos...")
    while True:
        try:
            time.sleep(5)
            client.reconnect()
            print("✅ Reconectado al broker")
            return
        except Exception as e:
            print(f"⚠️ Error al reconectar: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(BROKER, PORT, 60)
client.loop_forever()
