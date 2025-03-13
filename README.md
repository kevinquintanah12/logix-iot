# MQTT Simulator con Mosquitto

Este proyecto es un simulador MQTT utilizando **Mosquitto** como broker. Proporciona una forma sencilla de probar la publicación y suscripción de mensajes MQTT en un entorno local.

## 📌 Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Mosquitto**: Descárgalo e instálalo desde [aquí](https://mosquitto.org/download/).
- **Python** (opcional, si deseas ejecutar scripts relacionados).

## 📂 Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/kevinquintanah12/logix-iot.git
   cd logix-iot/mqtt-simulator
   ```

2. **Configurar Mosquitto**  
   Edita el archivo `config/mosquitto.conf` para asegurarte de que tenga la siguiente configuración básica:

   ```plaintext
   listener 1885
   allow_anonymous false
   password_file config/mosquitto_passwd
   log_dest file logs/mosquitto.log
   ```

3. **Crear usuarios para autenticación**  
   Si es la primera vez que configuras Mosquitto, ejecuta:

   ```bash
   mosquitto_passwd -c config/mosquitto_passwd usuario2
   ```

   Luego, ingresa la contraseña cuando se solicite.

## 🚀 Ejecutar el Broker MQTT

Para iniciar Mosquitto con la configuración definida, ejecuta:

```bash
mosquitto -c config/mosquitto.conf -v
```

- `-c config/mosquitto.conf`: Usa el archivo de configuración.
- `-v`: Muestra información detallada sobre las conexiones y mensajes.

Si todo está bien, Mosquitto comenzará a escuchar en el puerto `1885`.

## 📡 Probar Publicación y Suscripción

### 1️⃣ Suscribirse a un Tema

En una terminal, ejecuta:

```bash
mosquitto_sub -h localhost -p 1885 -t "mi/tema" -u "usuario2" -P "logix"
```

Esto suscribirá al cliente al tema `"mi/tema"`.

### 2️⃣ Publicar un Mensaje

En otra terminal, ejecuta:

```bash
mosquitto_pub -h localhost -p 1885 -t "mi/tema" -m "Hola MQTT!" -u "usuario2" -P "logix"
```

Si todo está funcionando correctamente, deberías ver `"Hola MQTT!"` aparecer en la terminal donde te suscribiste.

## 🛠 Solución de Problemas

1. **Error: `Connection Refused: not authorised`**  
   - Asegúrate de estar usando un usuario y contraseña correctos.  
   - Verifica que el archivo `mosquitto_passwd` esté en la ruta definida en `mosquitto.conf`.  

2. **Error: `Solo se permite un uso de cada dirección de socket`**  
   - Puede significar que Mosquitto ya se está ejecutando en el puerto 1885.  
   - Comprueba con:  
     ```bash
     netstat -ano | findstr :1885
     ```
   - Si ya hay un proceso en el puerto, deténlo antes de volver a ejecutar Mosquitto.

3. **Actualizar cambios desde GitHub sin perder archivos locales**  
   Si ves un error al hacer `git push`, prueba esto:

   ```bash
   git pull --rebase origin main
   git push origin main
   ```

   Si hay conflictos, revisa los cambios antes de hacer `git pull`.

## 📖 Referencias

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [Tutorial MQTT](https://www.hivemq.com/mqtt-essentials/)

---

¡Listo! Ahora tienes un entorno MQTT funcional para simulaciones. 🚀
```

Este `README.md` usa rutas relativas para que cualquier persona que clone el repositorio pueda ejecutarlo sin problemas. También incluye solución de errores comunes y referencias útiles.
