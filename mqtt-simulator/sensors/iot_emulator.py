#!/usr/bin/python 
import paho.mqtt.client as mqtt
import json
import time
import random
import threading

# Configuración del broker MQTT y tópicos
BROKER_URL = "localhost"
BROKER_PORT = 1883

# Tópicos MQTT
GPS_TOPIC    = "logix/gps"          # Datos provenientes del emulador de GPS
TEMP_TOPIC   = "logix/temperature"  # Sensor IoT de temperatura
HUM_TOPIC    = "logix/humidity"     # Sensor IoT de humedad
ALERT_TOPIC  = "logix/alerts"       # Tópico para alertas
CONFIG_TOPIC = "logix/config"       # Configuración inicial vía pub
ADJUST_TOPIC = "logix/adjustment"   # Ajustes manuales de temperatura vía pub
CONTROL_TOPIC= "logix/controliot"   # Comandos para encender/apagar el sensor

# Variables globales (se asignan vía pub)
current_temp = None         # Temperatura actual del sensor
current_hum  = None         # Humedad actual del sensor
TEMP_RANGE   = (None, None)   # Rango permitido de temperatura
HUM_RANGE    = (None, None)   # Rango permitido de humedad

# Variable para almacenar la última temperatura recibida vía GPS
gps_temp = None

# Flags de configuración y estado del sensor
configured = False
sensor_enabled = True       # Sensor encendido por defecto

# Bloqueo para acceso a variables globales
data_lock = threading.Lock()

# Callback de conexión MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("IoT Sensor: Conectado al broker MQTT.")
        client.subscribe(GPS_TOPIC)
        client.subscribe(CONFIG_TOPIC)
        client.subscribe(ADJUST_TOPIC)
        client.subscribe(CONTROL_TOPIC)
    else:
        print("IoT Sensor: Error de conexión, código:", rc)

# Callback para recepción de mensajes
def on_message(client, userdata, msg):
    global gps_temp, current_temp, current_hum, TEMP_RANGE, HUM_RANGE, configured, sensor_enabled
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
    except Exception as e:
        print("Error al decodificar mensaje en", msg.topic, ":", e)
        return

    if msg.topic == GPS_TOPIC:
        if "temperature" in data:
            try:
                new_gps_temp = float(data["temperature"])
                print("IoT Sensor: Recibida temperatura desde GPS:", new_gps_temp)
                with data_lock:
                    gps_temp = new_gps_temp
            except Exception as e:
                print("Error procesando temperatura GPS:", e)
    elif msg.topic == CONFIG_TOPIC:
        # Se espera que el mensaje incluya: current_temp, current_hum, temp_min, temp_max, hum_min, hum_max
        try:
            with data_lock:
                current_temp = float(data.get("current_temp"))
                current_hum = float(data.get("current_hum"))
                temp_min = float(data["temp_min"])
                temp_max = float(data["temp_max"])
                TEMP_RANGE = (temp_min, temp_max)
                hum_min = float(data["hum_min"])
                hum_max = float(data["hum_max"])
                HUM_RANGE = (hum_min, hum_max)
                configured = True
            print("IoT Sensor: Configuración inicial establecida:", {
                "current_temp": current_temp,
                "current_hum": current_hum,
                "TEMP_RANGE": TEMP_RANGE,
                "HUM_RANGE": HUM_RANGE
            })
        except Exception as e:
            print("Error en la configuración inicial:", e)
    elif msg.topic == ADJUST_TOPIC:
        # Se espera que el mensaje incluya "new_temp" para ajustar manualmente la temperatura
        try:
            if "new_temp" in data:
                new_temp = float(data["new_temp"])
                with data_lock:
                    if TEMP_RANGE[0] <= new_temp <= TEMP_RANGE[1]:
                        current_temp = new_temp
                        print("IoT Sensor: Ajuste manual de temperatura a:", new_temp)
                    else:
                        print("IoT Sensor: Valor de ajuste fuera del rango permitido:", new_temp)
            else:
                print("IoT Sensor: No se encontró 'new_temp' en el mensaje de ajuste.")
        except Exception as e:
            print("Error procesando ajuste manual:", e)
    elif msg.topic == CONTROL_TOPIC:
        # Se espera un mensaje con el campo "command": "on" o "off"
        try:
            if "command" in data:
                cmd = data["command"].strip().lower()
                with data_lock:
                    if cmd == "on":
                        sensor_enabled = True
                        print("IoT Sensor: Encendido manual (ON)")
                    elif cmd == "off":
                        sensor_enabled = False
                        print("IoT Sensor: Apagado manual (OFF)")
                    else:
                        print("IoT Sensor: Comando de control desconocido:", cmd)
            else:
                print("IoT Sensor: No se encontró 'command' en el mensaje de control.")
        except Exception as e:
            print("Error procesando comando de control:", e)
    else:
        print("Mensaje recibido en tópico desconocido:", msg.topic)

# Actualización de la temperatura del sensor
def update_sensor_temperature():
    global current_temp, gps_temp
    with data_lock:
        if sensor_enabled:
            if gps_temp is not None:
                # Ajuste gradual hacia la temperatura proveniente del GPS (50% del delta)
                delta = gps_temp - current_temp
                if abs(delta) < 0.1:
                    current_temp = gps_temp
                    gps_temp = None
                else:
                    current_temp += 0.5 * delta
            else:
                # Deriva aleatoria si no hay dato del GPS
                current_temp += random.uniform(-0.1, 0.1)

# Actualización de la humedad del sensor
def update_sensor_humidity():
    global current_hum
    with data_lock:
        if sensor_enabled:
            current_hum += random.uniform(-0.5, 0.5)
            if current_hum < HUM_RANGE[0]:
                current_hum = HUM_RANGE[0]
            elif current_hum > HUM_RANGE[1]:
                current_hum = HUM_RANGE[1]

# Publicación de datos en los tópicos correspondientes
def publish_sensor_data(client):
    with data_lock:
        if not configured or not sensor_enabled:
            return
    update_sensor_temperature()
    update_sensor_humidity()
    with data_lock:
        temp_val = round(current_temp, 2)
        hum_val  = round(current_hum, 2)
    # Publicar temperatura
    temp_data = {"temperature": temp_val}
    client.publish(TEMP_TOPIC, json.dumps(temp_data), qos=1, retain=True)
    print("IoT Sensor: Publicado", temp_data, "en", TEMP_TOPIC)
    
    # Publicar humedad
    hum_data = {"humidity": hum_val}
    client.publish(HUM_TOPIC, json.dumps(hum_data), qos=1, retain=True)
    print("IoT Sensor: Publicado", hum_data, "en", HUM_TOPIC)
    
    # Publicar alerta si la temperatura se sale del rango permitido
    with data_lock:
        if current_temp < TEMP_RANGE[0] or current_temp > TEMP_RANGE[1]:
            alert = {"alert": "Temperatura fuera de rango"}
            client.publish(ALERT_TOPIC, json.dumps(alert), qos=1, retain=True)
            print("IoT Sensor: Alerta publicada", alert)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_URL, BROKER_PORT, 60)
    except Exception as e:
        print("Error conectando al broker:", e)
        return

    client.loop_start()

    TIME_INTERVAL = 5  # Intervalo de publicación en segundos
    try:
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
