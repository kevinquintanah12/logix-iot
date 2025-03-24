# Usar la imagen oficial de Mosquitto como base
FROM eclipse-mosquitto:latest

# Establecer el directorio de trabajo para el proyecto
WORKDIR /mqtt-simulator

# Instalar dependencias necesarias para los emuladores en Python
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install paho-mqtt

# Crear el directorio donde se almacenarán los archivos de configuración
RUN mkdir -p /mqtt-simulator/config

# Copiar el archivo de configuración de Mosquitto
COPY mqtt-simulator/config/mosquitto.conf /mqtt-simulator/config/mosquitto.conf

# Copiar los scripts de emulador al contenedor
COPY mqtt-simulator/sensors /mqtt-simulator/sensors

# Exponer los puertos necesarios
EXPOSE 1883
EXPOSE 9001

# Ejecutar Mosquitto y los emuladores de sensores en segundo plano
CMD mosquitto -c /mqtt-simulator/config/mosquitto.conf -v & \
    python3 /mqtt-simulator/sensors/gps_emulator.py & \
    python3 /mqtt-simulator/sensors/iot_emulator.py & \
    tail -f /dev/null
