#  Simulador de Sensores IoT con MQTT

Este proyecto es un simulador de sensores **GPS, temperatura y humedad** utilizando **Mosquitto** como broker MQTT. Permite que la aplicación del chofer y otras aplicaciones reciban datos en tiempo real. Además, el chofer puede ajustar la temperatura manualmente para mantener condiciones óptimas en el transporte.

---

## 📌 Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Mosquitto**: Descárgalo e instálalo desde [aquí](https://mosquitto.org/download/).
- **Python 3** y las siguientes librerías:
  ```bash
  pip install paho-mqtt django-channels channels-redis
  ```
- **Git** para clonar el repositorio y trabajar en branches.

---

## 📂 Configuración del Entorno

1. **Clonar el repositorio y crear una rama de trabajo**
   ```bash
   git clone https://github.com/kevinquintanah12/logix-mqtt.git
   cd logix-mqtt/mqtt-simulator
   git checkout -b tu_rama
   ```

## 🚀 Iniciar el Broker MQTT

Ejecuta el siguiente comando para iniciar Mosquitto:

```bash
mosquitto -c config/mosquitto.conf -v
```

Si todo está bien, el broker comenzará a escuchar en el puerto `1885`.

Para probar la suscripción, asegúrate de pasar el usuario y la contraseña:

```bash
mosquitto_sub -h localhost -p 1885 -t "mi/tema" -u "usuario2" -P "logix"
```

---

## 📡 Implementación de Sensores y Cliente MQTT

Cada programador debe encargarse de su parte en una **rama separada**, asegurando que la **QoS sea prioritaria** para garantizar la confiabilidad de los datos.

### 🔹 Cliente MQTT (`client.py`)
Debe manejar la suscripción a los topics de **GPS, temperatura y humedad** y permitir que el chofer ajuste manualmente la temperatura. Se recomienda usar `paho-mqtt`.

### 🔹 Sensores MQTT (`sensors.py`)
Debe publicar datos simulados en los topics **logix/gps, logix/temperatura y logix/humedad**, asegurando que la temperatura y la humedad cambien dinámicamente según condiciones predefinidas.

## 🔄 Integración con WebSockets

Para recibir y mostrar datos en tiempo real en Django, configuramos `django-channels` y WebSockets. 

### 🔹 Configuración de `settings.py`
```python
INSTALLED_APPS = [
    'channels',
    'mi_app',  # Reemplaza con el nombre de tu app
]

ASGI_APPLICATION = "mi_proyecto.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # Usa Redis en producción
    },
}
```
### 🔹 WebSocket Consumer (`consumers.py`)



```

Con esto, la aplicación puede recibir datos en tiempo real y mostrarlos en el frontend.

---

## 📖 Flujo de Trabajo en Git

1. **Crear tu branch**  
   ```bash
   git checkout -b feature_nombre
   ```
2. **Realizar cambios y confirmar**  
   ```bash
   git add .
   git commit -m "Implementación del sensor de temperatura"
   ```
3. **Actualizar con la rama principal antes de hacer push**  
   ```bash
   git pull --rebase origin main
   ```
4. **Subir cambios y crear un PR**  
   ```bash
   git push origin feature_nombre
   ```

---

## 🛠 Solución de Problemas

1. **Error de autenticación (`Connection Refused: not authorised`)**
   - Usa el usuario y contraseña correctos.
   - Verifica que `mosquitto_passwd` esté bien configurado.

2. **Mosquitto ya está ejecutándose en el puerto 1885**
   - Verifica procesos en el puerto con:
     ```bash
     netstat -ano | findstr :1885  # Windows
     lsof -i :1885  # Linux/Mac
     ```
   - Detén el proceso antes de reiniciar Mosquitto.

---

## 📖 Referencias

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [Tutorial MQTT](https://www.hivemq.com/mqtt-essentials/)
- [Django Channels](https://channels.readthedocs.io/en/latest/)

