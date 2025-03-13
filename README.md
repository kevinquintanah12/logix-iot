#  Simulador de Sensores IoT con MQTT

Este proyecto es un simulador de sensores **GPS, temperatura y humedad** utilizando **Mosquitto** como broker MQTT. Permite que la aplicación del chofer y otras aplicaciones reciban datos en tiempo real. Además, el chofer puede ajustar la temperatura manualmente para mantener condiciones óptimas en el transporte.

---

## 📌 Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Mosquitto**: Descárgalo e instálalo desde [aquí](https://mosquitto.org/download/).
- **Python ** y las siguientes librerías:
  ```bash
  pip install paho-mqtt django-channels channels-redis
  ```
- **Git** para clonar el repositorio y trabajar en branches.

---
## Cómo añadir Mosquitto al PATH

## Windows

1. Instala Mosquitto desde el sitio oficial: [https://mosquitto.org/download/](https://mosquitto.org/download/).
2. Abre el Explorador de archivos y busca la carpeta donde se instaló Mosquitto (por defecto suele estar en `C:\Program Files\mosquitto`).
3. Copia la ruta de la carpeta `mosquitto`.
4. Abre el menú de inicio y busca **Editar las variables de entorno del sistema**.
5. En la ventana que se abre, haz clic en **Variables de entorno...**.
6. En la sección **Variables del sistema**, busca y selecciona la variable `Path` y haz clic en **Editar**.
7. Haz clic en **Nuevo** y pega la ruta copiada anteriormente.
8. Presiona **Aceptar** en todas las ventanas y reinicia la terminal o el sistema.
9. Verifica la instalación ejecutando en la terminal:
   ```sh
   mosquitto -v
   ```

## Linux/Mac

1. Instala Mosquitto:
   ```sh
   # Ubuntu/Debian
   sudo apt update && sudo apt install -y mosquitto mosquitto-clients
   
   # macOS (Homebrew)
   brew install mosquitto
   ```
2. Encuentra la ruta de Mosquitto ejecutando:
   ```sh
   which mosquitto
   ```
3. Añade la ruta al `PATH`:
   ```sh
   export PATH=$PATH:/usr/local/sbin:/usr/sbin:/sbin
   ```
   Si Mosquitto está en otra ubicación, ajusta la ruta en el comando.
4. Para hacer esto permanente, agrega la línea anterior al archivo de configuración de tu shell:
   ```sh
   echo 'export PATH=$PATH:/usr/local/sbin:/usr/sbin:/sbin' >> ~/.bashrc  # Para Bash
   echo 'export PATH=$PATH:/usr/local/sbin:/usr/sbin:/sbin' >> ~/.zshrc   # Para Zsh
   ```
5. Aplica los cambios con:
   ```sh
   source ~/.bashrc  # Para Bash
   source ~/.zshrc   # Para Zsh
   ```
6. Verifica la instalación ejecutando:
   ```sh
   mosquitto -v
   ```

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





Con esto, la aplicación puede recibir datos en tiempo real y mostrarlos en el frontend.



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
   git push origin tu_rama
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

