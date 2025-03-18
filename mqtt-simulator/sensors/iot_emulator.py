#!/usr/bin/python
import paho.mqtt.client as mqtt
import json
import time
import random

# Configuración del broker MQTT y tópicos
BROKER_URL = "localhost"
BROKER_PORT = 1883

# Tópicos para la suscripción y publicación
GPS_TOPIC = "logix/gps"             # Datos publicados por el emulador de GPS
TEMP_TOPIC = "logix/temperature"     # Sensor IoT de temperatura
HUM_TOPIC = "logix/humidity"         # Sensor IoT de humedad
ALERT_TOPIC = "logix/alerts"         # Tópico para alertas

# Configuración del sensor IoT
TEMP_RANGE = (2.0, 10.0)             # Rango permitido de temperatura (°C)
HUM_RANGE = (40.0, 95.0)             # Rango permitido de humedad (%)
current_temp = 5.0                   # Temperatura inicial del sensor
current_hum = 60.0                   # Humedad inicial del sensor

# Variable para almacenar la última temperatura recibida del GPS
gps_temp = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("IoT Sensor: Conectado al broker MQTT.")
        # Se suscribe al tópico donde se publican los datos del GPS
        client.subscribe(GPS_TOPIC)
    else:
        print("IoT Sensor: Error de conexión, código:", rc)

def on_message(client, userdata, msg):
    global gps_temp
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        # Se asume que el mensaje del GPS incluye el campo "temperature"
        if "temperature" in data:
            new_gps_temp = data["temperature"]
            print("IoT Sensor: Recibida temperatura desde GPS:", new_gps_temp)
            gps_temp = new_gps_temp
    except Exception as e:
        print("IoT Sensor: Error procesando el mensaje GPS:", e)

def update_sensor_temperature():
    """
    Actualiza la temperatura del sensor IoT.
    Si se ha recibido una temperatura del GPS, se realiza una transición
    suave (por ejemplo, aplicando una fracción del delta) hacia ese valor.
    Luego se ajusta para que permanezca dentro del rango permitido.
    """
    global current_temp, gps_temp
    if gps_temp is not None:
        # Se calcula la diferencia entre la temperatura del GPS y la actual
        delta = gps_temp - current_temp
        # Se actualiza de forma gradual (por ejemplo, el 50% de la diferencia)
        current_temp += 0.5 * delta
    else:
        # Si no se recibió dato del GPS, se puede aplicar un pequeño deriva aleatoria
        current_temp += random.uniform(-0.1, 0.1)

    # Se asegura que la temperatura se mantenga dentro de los límites
    if current_temp < TEMP_RANGE[0]:
        current_temp = TEMP_RANGE[0]
    elif current_temp > TEMP_RANGE[1]:
        current_temp = TEMP_RANGE[1]

def update_sensor_humidity():
    """
    Simula pequeños cambios en la humedad.
    """
    global current_hum
    current_hum += random.uniform(-0.5, 0.5)
    if current_hum < HUM_RANGE[0]:
        current_hum = HUM_RANGE[0]
    elif current_hum > HUM_RANGE[1]:
        current_hum = HUM_RANGE[1]

def publish_sensor_data(client):
    """
    Actualiza y publica los datos de temperatura y humedad del sensor IoT.
    También publica una alerta si la temperatura se sale del rango.
    """
    update_sensor_temperature()
    update_sensor_humidity()
    
    # Publicar temperatura
    temp_data = {"temperature": round(current_temp, 2)}
    client.publish(TEMP_TOPIC, json.dumps(temp_data), qos=1, retain=True)
    print("IoT Sensor: Publicado", temp_data, "en", TEMP_TOPIC)
    
    # Publicar humedad
    hum_data = {"humidity": round(current_hum, 2)}
    client.publish(HUM_TOPIC, json.dumps(hum_data), qos=1, retain=True)
    print("IoT Sensor: Publicado", hum_data, "en", HUM_TOPIC)
    
    # Publicar alerta si la temperatura está fuera del rango
    if current_temp < TEMP_RANGE[0] or current_temp > TEMP_RANGE[1]:
        alert = {"alert": "Temperatura fuera de rango"}
        client.publish(ALERT_TOPIC, json.dumps(alert), qos=1, retain=True)
        print("IoT Sensor: Alerta publicada", alert)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(BROKER_URL, BROKER_PORT, 60)
    client.loop_start()
    
    try:
        # Bucle principal de publicación: cada TIME_INTERVAL segundos se actualizan y publican los datos
        TIME_INTERVAL = 5
        while True:
            publish_sensor_data(client)
            time.sleep(TIME_INTERVAL)
    except KeyboardInterrupt:
        print("IoT Sensor: Interrumpido por el usuario.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
