# MQTT Simulator con Mosquitto

Este proyecto simula un sistema MQTT usando **Mosquitto** como broker MQTT. Aquí encontrarás instrucciones sobre cómo configurar, ejecutar y probar el sistema.

---

## Requisitos previos

Antes de comenzar, asegúrate de tener instalados los siguientes requisitos:

1. **Mosquitto**: El broker MQTT que utilizamos. Puedes descargarlo desde [aquí](https://mosquitto.org/download/).
2. **Python**: Se recomienda usar un entorno virtual (`venv`) para manejar dependencias.
3. **Archivo de Contraseña** (`mosquitto_passwd`): Para autenticar a los usuarios.

---

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/kevinquintanah12/logix-iot.git
cd logix-iot/mqtt-simulator
2. Crear un Entorno Virtual (Opcional, pero recomendado)
bash
Copiar
Editar
python -m venv venv
source venv/bin/activate  # En macOS/Linux
venv\Scripts\activate     # En Windows
3. Configurar Mosquitto
Asegúrate de tener un archivo de configuración mosquitto.conf en la carpeta config/, con un contenido similar a este:

plaintext
Copiar
Editar
listener 1885
allow_anonymous false
password_file config/mosquitto_passwd
log_dest file logs/mosquitto.log
La línea allow_anonymous false obliga a que los clientes se autentiquen.

4. Crear Usuarios para Autenticación
Para crear un usuario en el archivo mosquitto_passwd, usa el siguiente comando:

bash
Copiar
Editar
mosquitto_passwd -c config/mosquitto_passwd usuario2
Te pedirá que ingreses una contraseña. En este ejemplo, el usuario es usuario2 y la contraseña puede ser "logix".

Si quieres agregar más usuarios, usa:

bash
Copiar
Editar
mosquitto_passwd config/mosquitto_passwd otro_usuario
Ejecución del Broker Mosquitto
Para iniciar el broker Mosquitto, usa:

bash
Copiar
Editar
mosquitto -c config/mosquitto.conf -v
Explicación:

-c config/mosquitto.conf: Especifica el archivo de configuración.
-v: Muestra los mensajes detallados de lo que está ocurriendo en el broker.
Mosquitto se ejecutará en el puerto 1885 y permitirá la autenticación con el archivo mosquitto_passwd.

Pruebas: Publicar y Suscribirse a un Tema
1. Suscribirse a un Tema (Subscriber)
Abre una terminal y usa este comando para suscribirte al tema "mi/tema":

bash
Copiar
Editar
mosquitto_sub -h localhost -p 1885 -t "mi/tema" -u "usuario2" -P "logix"
Explicación:

-h localhost: Conectarse al broker Mosquitto en tu máquina.
-p 1885: Puerto en el que Mosquitto está escuchando.
-t "mi/tema": Tema al que te suscribes.
-u "usuario2": Nombre de usuario.
-P "logix": Contraseña del usuario.
Este comando permanecerá escuchando los mensajes publicados en "mi/tema".

2. Publicar un Mensaje (Publisher)
En otra terminal, usa este comando para enviar un mensaje al tema "mi/tema":

bash
Copiar
Editar
mosquitto_pub -h localhost -p 1885 -t "mi/tema" -m "Hola, este es un mensaje MQTT!" -u "usuario2" -P "logix"
Explicación:

-h localhost: Conectar al broker local.
-p 1885: Puerto de Mosquitto.
-t "mi/tema": Tema en el que se publicará el mensaje.
-m "Hola, este es un mensaje MQTT!": Mensaje que se enviará.
-u "usuario2" y -P "logix": Usuario y contraseña para autenticación.
Si la configuración es correcta, deberías ver el mensaje reflejado en la terminal del Subscriber.

Solución de Problemas
1. Mosquitto no inicia o muestra "Solo se permite un uso de cada dirección de socket"
Posible causa: El puerto 1883 o 1885 ya está en uso.

Solución:

bash
Copiar
Editar
netstat -ano | findstr :1885
Si aparece un proceso usando el puerto, deténlo con:

bash
Copiar
Editar
taskkill /PID <PID> /F
2. Error de autenticación al suscribirse o publicar
Asegúrate de haber creado correctamente el archivo mosquitto_passwd.
Verifica que allow_anonymous false está en el archivo mosquitto.conf.
Revisa el usuario y la contraseña.
3. Cambiar el Puerto
Si necesitas cambiar el puerto (por ejemplo, si 1885 está ocupado), edita config/mosquitto.conf:

plaintext
Copiar
Editar
listener 1886
Luego, reinicia Mosquitto y usa el puerto nuevo en los comandos.

Contribuciones
Si deseas contribuir con mejoras, puedes hacer un fork del repositorio y enviar un pull request.

Notas Finales
Asegúrate de que Mosquitto está en ejecución antes de publicar o suscribirte.
Usa mosquitto_sub y mosquitto_pub en diferentes terminales para probar la comunicación.
Puedes crear múltiples temas para simular diferentes sensores y dispositivos IoT.
bash
Copiar
Editar

Este README es más adaptable para cualquier usuario que clone el proyecto, ya que usa rutas relativas e
