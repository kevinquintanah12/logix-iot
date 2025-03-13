import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "logix/gps"

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.on_message = on_message

print(f"Escuchando en {TOPIC}...")
client.loop_forever()
