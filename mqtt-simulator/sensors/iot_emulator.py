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
TEMP_RANGE   = (None, None)   # Rango permitido de temperatura (min, max)
HUM_RANGE    = (None, None)   # Rango permitido de humedad (min, max)

# Variable para almacenar la última temperatura recibida vía GPS (solo para referencia)
gps_temp = None

# Flags de configuración y estado del sensor
configured = False
sensor_enabled = True       # Sensor encendido por defecto

# Flag para indicar que el usuario ajustó manualmente la temperatura,
# de forma que se congela la actualización automática
manual_adjust = False

# Flag que indica que la temperatura se salió del rango y se requiere ajuste manual
require_adjustment = False

# Flag para evitar el envío excesivo de alertas
alert_published = False

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
    global gps_temp, current_temp, current_hum, TEMP_RANGE, HUM_RANGE
    global configured, sensor_enabled, manual_adjust, require_adjustment, alert_published
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
    except Exception as e:
        print("Error al decodificar mensaje en", msg.topic, ":", e)
        return

    if msg.topic == GPS_TOPIC:
        # Se recibe la temperatura proveniente del GPS solo para registro
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
                # Al configurar, se restablecen las banderas de ajuste
                manual_adjust = False
                require_adjustment = False
                alert_published = False
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
                    if TEMP_RANGE[0] is not None and TEMP_RANGE[1] is not None:
                        current_temp = new_temp
                        manual_adjust = True
                        # Si el nuevo valor está dentro del rango, se indica que la temperatura fue reestablecida.
                        if TEMP_RANGE[0] <= new_temp <= TEMP_RANGE[1]:
                            require_adjustment = False
                            alert_published = False
                            print("IoT Sensor: Ajuste manual realizado. Temperatura reestablecida a:", new_temp)
                            reestablished = {"status": "Temperatura reestablecida", "temperature": current_temp}
                            client.publish(ALERT_TOPIC, json.dumps(reestablished), qos=1, retain=True)
                        else:
                            # Se acepta el ajuste aunque esté fuera del rango y se publica alerta.
                            require_adjustment = True
                            print("IoT Sensor: Ajuste manual realizado. Valor de ajuste fuera del rango permitido:", new_temp)
                            alert = {"alert": "Temperatura fuera de rango, ajuste requerido", "temperature": current_temp}
                            client.publish(ALERT_TOPIC, json.dumps(alert), qos=1, retain=True)
                    else:
                        print("IoT Sensor: Rango de temperatura no definido.")
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
            print("IoT Sensor: Error procesando comando de control:", e)
    else:
        print("Mensaje recibido en tópico desconocido:", msg.topic)

# Actualización de la temperatura del sensor
# Se aplica un 80% de probabilidad para deriva normal y un 20% para deriva mayor.
def update_sensor_temperature():
    global current_temp, require_adjustment
    with data_lock:
        if sensor_enabled and not manual_adjust and not require_adjustment:
            if random.random() < 0.2:  # 20% evento de deriva mayor
                drift = random.uniform(-0.5, 0.5)
                print("IoT Sensor: Evento de deriva mayor:", drift)
            else:  # 80% deriva normal
                drift = random.uniform(-0.05, 0.05)
            new_temp = current_temp + drift
            if TEMP_RANGE[0] is not None and TEMP_RANGE[1] is not None:
                if new_temp < TEMP_RANGE[0] or new_temp > TEMP_RANGE[1]:
                    require_adjustment = True
                    print("IoT Sensor: Temperatura fuera del rango (nuevo valor:", round(new_temp,2),
                          ") - se requiere ajuste manual.")
                else:
                    current_temp = new_temp
            else:
                current_temp = new_temp

# Actualización de la humedad del sensor
def update_sensor_humidity():
    global current_hum
    with data_lock:
        if sensor_enabled:
            current_hum += random.uniform(-0.5, 0.5)
            if HUM_RANGE[0] is not None and current_hum < HUM_RANGE[0]:
                current_hum = HUM_RANGE[0]
            elif HUM_RANGE[1] is not None and current_hum > HUM_RANGE[1]:
                current_hum = HUM_RANGE[1]

# Publicación de datos en los tópicos correspondientes
def publish_sensor_data(client):
    global alert_published
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
    
    # Publicar alerta si la temperatura está fuera del rango
    with data_lock:
        if TEMP_RANGE[0] is not None and TEMP_RANGE[1] is not None:
            if current_temp < TEMP_RANGE[0] or current_temp > TEMP_RANGE[1]:
                if not alert_published:
                    alert = {"alert": "Temperatura fuera de rango, ajuste requerido", "temperature": temp_val}
                    client.publish(ALERT_TOPIC, json.dumps(alert), qos=1, retain=True)
                    print("IoT Sensor: Alerta publicada", alert)
                    alert_published = True
            else:
                alert_published = False

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
