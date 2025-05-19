
import paho.mqtt.client as mqtt
import json
import time
import random
import threading

# Configuración del broker MQTT y tópicos
BROKER_URL    = "localhost"
BROKER_PORT   = 1883

# Tópicos MQTT
temp_topic    = "logix/temperature"
hum_topic     = "logix/humidity"
alert_topic   = "logix/alerts"
config_topic  = "logix/config"
adjust_topic  = "logix/adjustment"
control_topic = "logix/controliot"

# Bloqueos y sincronización
data_lock     = threading.Lock()
config_event  = threading.Event()

# Estado del sensor
t_current      = None
current_hum    = None
TEMP_RANGE     = (18.0, 25.0)  # valores por defecto
HUM_RANGE      = (30.0, 70.0)
sensor_enabled = True
manual_adjust  = False
require_adjust  = False
alert_sent     = False
configured     = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        client.subscribe([(config_topic, 0), (adjust_topic, 0), (control_topic, 0)])
    else:
        print(f"Error de conexión: {rc}")


def on_message(client, userdata, msg):
    global t_current, current_hum, TEMP_RANGE, HUM_RANGE
    global sensor_enabled, manual_adjust, require_adjust, alert_sent, configured

    try:
        data = json.loads(msg.payload.decode('utf-8'))
    except:
        return

    if msg.topic == config_topic:
        with data_lock:
            # Actualiza temperatura si viene
            if 'current_temp' in data:
                t_current = float(data['current_temp'])
            # Actualiza rangos si vienen
            if 'temp_min' in data and 'temp_max' in data:
                TEMP_RANGE = (float(data['temp_min']), float(data['temp_max']))
            if 'current_hum' in data:
                current_hum = float(data['current_hum'])
            if 'hum_min' in data and 'hum_max' in data:
                HUM_RANGE = (float(data['hum_min']), float(data['hum_max']))
            configured = True
            sensor_enabled = True
            manual_adjust = False
            require_adjust = False
            alert_sent = False
            print("Configuración recibida:", data)
            # Al cambiar temperatura, comprueba fuera de rango
            if 'current_temp' in data:
                t = t_current
                if t < TEMP_RANGE[0] or t > TEMP_RANGE[1]:
                    require_adjust = True
                    payload = json.dumps({
                        'alert': 'temperatura fuera de rango en configuración',
                        'temperature': t
                    })
                    client.publish(alert_topic, payload, qos=1, retain=True)
                    print(f"Publicando ALERTA en {alert_topic}: {payload}")
        config_event.set()

    elif msg.topic == adjust_topic and 'new_temp' in data:
        try:
            new_t = float(data['new_temp'])
            with data_lock:
                t_current = new_t
                manual_adjust = True
                require_adjust = not (TEMP_RANGE[0] <= new_t <= TEMP_RANGE[1])
                status = {'temperature': new_t, 'status': 'adjusted', 'in_range': not require_adjust}
            client.publish(alert_topic, json.dumps(status), qos=1, retain=True)
            print(f"Publicando ajuste: {status}")
        except Exception as e:
            print(f"Error en ajuste: {e}")

    elif msg.topic == control_topic and 'command' in data:
        cmd = data['command'].lower().strip()
        with data_lock:
            sensor_enabled = (cmd == 'on')
        print(f"Sensor {'ENCENDIDO' if sensor_enabled else 'APAGADO'}")


def update_temperature():
    global t_current, require_adjust
    with data_lock:
        if not (configured and sensor_enabled and not manual_adjust and not require_adjust):
            return
        drift = random.uniform(-0.5, 0.5) if random.random() < 0.2 else random.uniform(-0.05, 0.05)
        new_t = t_current + drift
        if TEMP_RANGE[0] <= new_t <= TEMP_RANGE[1]:
            t_current = new_t
        else:
            require_adjust = True
            print(f"Deriva fuera de rango: {round(new_t,2)}")


def update_humidity():
    global current_hum
    with data_lock:
        if not (configured and sensor_enabled):
            return
        current_hum += random.uniform(-0.5, 0.5)
        current_hum = min(max(current_hum, HUM_RANGE[0]), HUM_RANGE[1])


def publish_data(client):
    global alert_sent
    with data_lock:
        if not (configured and sensor_enabled):
            return
    update_temperature()
    update_humidity()
    with data_lock:
        t = round(t_current,2)
        h = round(current_hum,2)
    p_temp = json.dumps({'temperature': t})
    p_hum  = json.dumps({'humidity': h})
    client.publish(temp_topic, p_temp, qos=1, retain=True)
    print(f"Publicando en {temp_topic}: {p_temp}")
    client.publish(hum_topic, p_hum, qos=1, retain=True)
    print(f"Publicando en {hum_topic}: {p_hum}")
    with data_lock:
        if require_adjust and not alert_sent:
            alt = json.dumps({'alert': 'ajuste requerido', 'temperature': t})
            client.publish(alert_topic, alt, qos=1, retain=True)
            print(f"Publicando ALERTA en {alert_topic}: {alt}")
            alert_sent = True


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER_URL, BROKER_PORT, 60)
    except Exception as e:
        print(f"Error conectando al broker: {e}")
        return
    client.loop_start()
    print(f"Esperando CONFIG en {config_topic}…")
    config_event.wait()
    print("¡Listo! Publicando cada 5 s…")
    try:
        while True:
            publish_data(client)
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()
