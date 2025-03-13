# 🚚 LogiX - Simulador IoT con MQTT

Este proyecto tiene como objetivo emular sensores de **GPS, temperatura y humedad** mediante MQTT, permitiendo que la **App del Chofer** y otras aplicaciones puedan recibir datos en tiempo real. Además, el chofer podrá ajustar la temperatura en función del clima para optimizar el transporte de productos.

---

## 📌 Configuración del Broker MQTT con Mosquitto

Soy responsable de configurar el **broker MQTT** utilizando **Mosquitto**. Ustedes deberán encargarse de los sensores, el cliente MQTT y la configuración de la QoS para garantizar la prioridad de los mensajes.

### 🔹 Instalación de Mosquitto

1. Instala **Mosquitto** en tu sistema:
   ```bash
   sudo apt update && sudo apt install -y mosquitto mosquitto-clients
   ```

2. Verifica la instalación:
   ```bash
   mosquitto -v
   ```

### 🔹 Configuración del Broker

1. Clona el repositorio y entra en el directorio:
   ```bash
   git clone https://github.com/kevinquintanah12/logix-iot.git
   cd logix-iot/mqtt-simulator
   ```

2. Edita el archivo de configuración `config/mosquitto.conf` con lo siguiente:
   ```plaintext
   listener 1883
   allow_anonymous false
   password_file config/mosquitto_passwd
   log_dest file logs/mosquitto.log
   ```

3. Crea usuarios para autenticación:
   ```bash
   mosquitto_passwd -c config/mosquitto_passwd usuario_mqtt
   ```

4. Inicia el broker:
   ```bash
   mosquitto -c config/mosquitto.conf -v
   ```

---

## 📡 Configuración del Cliente MQTT y Sensores (Responsabilidad de los demás programadores)

Ustedes deberán desarrollar los sensores y el cliente MQTT siguiendo estas instrucciones:

### 🔹 1️⃣ Clonar el repositorio y crear su branch

Cada programador debe trabajar en su propia branch:
   ```bash
   git checkout -b feature/nombre-tarea
   ```

### 🔹 2️⃣ Crear el cliente MQTT (`client.py`)

El cliente MQTT se encargará de suscribirse a los topics relevantes y recibir datos de los sensores.

#### 📜 Ejemplo de `client.py`
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.username_pw_set("usuario_mqtt", "password")
client.connect("localhost", 1883, 60)
client.subscribe("logix/sensores/#")
client.on_message = on_message
client.loop_forever()
```

### 🔹 3️⃣ Emulación de Sensores

Cada sensor debe publicar datos en los topics correspondientes. Aquí hay ejemplos:

#### 🛰️ GPS (emulación de movimiento)
```python
import paho.mqtt.client as mqtt
import json, time

def generar_gps():
    lat, lon, speed = 19.4326, -99.1332, 60
    return json.dumps({"lat": lat, "lon": lon, "speed": speed})

client = mqtt.Client()
client.username_pw_set("usuario_mqtt", "password")
client.connect("localhost", 1883, 60)

while True:
    client.publish("logix/sensores/gps", generar_gps())
    time.sleep(5)
```

#### 🌡️ Temperatura (chofer puede ajustar valores)
```python
import paho.mqtt.client as mqtt
import json, time, random

def generar_temperatura():
    valor = random.uniform(0, 30)  # Simulación de cambios climáticos
    return json.dumps({"valor": valor, "unidad": "C"})

client = mqtt.Client()
client.username_pw_set("usuario_mqtt", "password")
client.connect("localhost", 1883, 60)

while True:
    client.publish("logix/sensores/temperatura", generar_temperatura())
    time.sleep(10)
```

#### 💧 Humedad
```python
import paho.mqtt.client as mqtt
import json, time, random

def generar_humedad():
    valor = random.uniform(20, 80)
    return json.dumps({"valor": valor, "unidad": "%"})

client = mqtt.Client()
client.username_pw_set("usuario_mqtt", "password")
client.connect("localhost", 1883, 60)

while True:
    client.publish("logix/sensores/humedad", generar_humedad())
    time.sleep(10)
```

---

## 🔧 Configuración de QoS (Calidad de Servicio)

Para garantizar la prioridad de los mensajes:
- **QoS 2** para datos críticos como temperatura y humedad.
- **QoS 1** para GPS, ya que su actualización es frecuente pero menos crítica.

Ejemplo de publicación con QoS en Python:
```python
client.publish("logix/sensores/temperatura", generar_temperatura(), qos=2)
```

---

## 🔄 Flujo de Trabajo con Git

1. **Clonar el repositorio y cambiar a su branch**
   ```bash
   git checkout -b feature/nombre-tarea
   ```
2. **Desarrollar el código y hacer commits**
   ```bash
   git add .
   git commit -m "Añadido sensor de temperatura"
   ```
3. **Subir los cambios**
   ```bash
   git push origin feature/nombre-tarea
   ```
4. **Crear un Pull Request en GitHub** para revisión y fusión con `main`.

---

## 🚀 Pruebas Finales

Una vez que todo esté implementado, prueba el flujo completo:
1. **Inicia el broker MQTT**
   ```bash
   mosquitto -c config/mosquitto.conf -v
   ```
2. **Ejecuta los sensores** en diferentes terminales.
3. **Ejecuta el cliente MQTT** para verificar que los datos llegan correctamente.

Si todo está correcto, la app del chofer y otras aplicaciones podrán recibir los datos de temperatura, humedad y GPS en tiempo real. 🎯


