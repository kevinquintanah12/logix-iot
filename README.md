# MQTT Simulator con Mosquitto

Este proyecto simula un sistema MQTT usando **Mosquitto** como broker MQTT. Aquí encontrarás instrucciones sobre cómo configurar, ejecutar y probar el sistema.

### Requisitos previos

Antes de comenzar, asegúrate de tener instalados los siguientes requisitos:

1.  **Mosquitto**: El broker MQTT que utilizamos.
2.  **Python**: Se recomienda usar un entorno virtual (`venv`) para manejar dependencias.
3.  **Archivo de Contraseña** (`mosquitto_passwd`): Para autenticar a los usuarios.

---

### Configuración

1.  **Descargar Mosquitto**: Si aún no tienes Mosquitto, descárgalo e instálalo desde el sitio oficial: Descargar Mosquitto
    
2.  **Configurar Mosquitto**: Asegúrate de tener un archivo de configuración `mosquitto.conf` que especifique el puerto de escucha y el archivo de contraseñas. Un ejemplo de configuración sería:
    
    ```plaintext
    listener 1885
    allow_anonymous false
    password_file C:/Users/Kevin/mqtt-simulator/mqtt-simulator/config/mosquitto_passwd
    log_dest file C:/Users/Kevin/mqtt-simulator/mqtt-simulator/logs/mosquitto.log
    ```

    La configuración `allow_anonymous false` asegura que los usuarios deban autenticarse.
    
3.  **Crear usuarios**: Usa el siguiente comando para crear un usuario en el archivo `mosquitto_passwd`:
    
    ```bash
    mosquitto_passwd -c C:/Users/Kevin/mqtt-simulator/mqtt-simulator/config/mosquitto_passwd usuario2
    ```

    Te pedirá que ingreses una contraseña para el usuario. En este ejemplo, el usuario creado es `usuario2` con la contraseña `logix`.

---

### Ejecución de Mosquitto

Para iniciar el broker Mosquitto con tu archivo de configuración, ejecuta el siguiente comando:

```bash
mosquitto -c C:/Users/Kevin/mqtt-simulator/mqtt-simulator/config/mosquitto.conf -v
