#!/usr/bin/python
import paho.mqtt.client as mqtt
import json
import time

# Configuración del broker MQTT y tópicos
BROKER_URL = "localhost"
BROKER_PORT = 1885

# Tópicos MQTT
TEMP_TOPIC = "logix/temperature"

# Rango de temperatura permitido
TEMP_RANGE = (2.0, 10.0)

# Estado del sensor
current_temp = 5.0  # Temperatura inicial
target_temp = None   # Temperatura objetivo
STEPS = 10           # Número de pasos para cambio gradual
step_counter = 0     # Contador de pasos

# Conexión al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT.")
        client.subscribe(TEMP_TOPIC)
    else:
        print(f"❌ Error de conexión, código: {rc}")

# Recepción de mensaje MQTT
def on_message(client, userdata, msg):
    global target_temp, step_counter
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        if "temperature" in data:
            new_temp = float(data["temperature"])
            if TEMP_RANGE[0] <= new_temp <= TEMP_RANGE[1]:
                print(f"📡 Temperatura recibida por MQTT: {new_temp}°C")
                target_temp = new_temp
                step_counter = 0  # Reiniciar ajuste gradual
            else:
                print(f"⚠️ Temperatura fuera de rango: {TEMP_RANGE}")
    except Exception as e:
        print(f"❌ Error procesando mensaje MQTT: {e}")

# Desconexión del broker
def on_disconnect(client, userdata, rc):
    print("🔄 Desconectado del broker MQTT. Intentando reconectar...")
    client.reconnect()

# Cambio gradual de temperatura
def update_temperature():
    global current_temp, target_temp, step_counter
    if target_temp is not None:
        delta = target_temp - current_temp
        if abs(delta) < 0.01:  # Si la diferencia es mínima, fijar la temperatura
            current_temp = target_temp
            target_temp = None
        else:
            gradual_step = delta / STEPS
            current_temp += gradual_step
            step_counter += 1
            if step_counter >= STEPS:
                current_temp = target_temp
                target_temp = None

# Entrada manual desde la terminal
def manual_temperature_adjustment():
    global target_temp, step_counter
    try:
        manual_temp = float(input("🔧 Ingresa la nueva temperatura: "))
        if TEMP_RANGE[0] <= manual_temp <= TEMP_RANGE[1]:
            print(f"✅ Ajustando temperatura manualmente a {manual_temp}°C")
            target_temp = manual_temp
            step_counter = 0  # Reiniciar ajuste gradual
        else:
            print(f"⚠️ Temperatura fuera de rango: {TEMP_RANGE}")
    except ValueError:
        print("❌ Ingresa un número válido.")

# Publicación de temperatura
def publish_sensor_data(client):
    update_temperature()
    temp_data = {"temperature": round(current_temp, 2)}
    client.publish(TEMP_TOPIC, json.dumps(temp_data), qos=1, retain=True)
    print(f"📤 Publicado: {temp_data} en {TEMP_TOPIC}")

# Función principal
def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(BROKER_URL, BROKER_PORT, 60)
    client.loop_start()

    try:
        while True:
            manual_temperature_adjustment()  # Entrada manual desde la terminal
            for _ in range(STEPS):
                publish_sensor_data(client)
                time.sleep(1)  # Esperar 1 segundo entre cambios graduales
    except KeyboardInterrupt:
        print("🛑 Interrumpido por el usuario.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()


