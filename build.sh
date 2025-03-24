#!/bin/bash 

# Actualizar los repositorios e instalar Mosquitto
apt-get update && apt-get install -y mosquitto mosquitto-clients

# Crear el directorio de trabajo y la carpeta de configuración
mkdir -p /mqtt-simulator/config

# Copiar el archivo de configuración de Mosquitto (ajusta la ruta al archivo)
cp mqtt-simulator/config/mosquitto.conf /mqtt-simulator/config/mosquitto.conf

# Modificar la configuración de Mosquitto si es necesario
# Aquí puedes agregar configuraciones adicionales si es necesario
# por ejemplo, cambiar la ruta de los puertos, o agregar loggers

# Exponer los puertos necesarios
# Render automáticamente expone puertos según lo configurado
# Si usas un servidor local, asegúrate de tener permisos para abrir los puertos
# No es necesario definir EXPOSE en un script como en Docker

# Iniciar el servicio de Mosquitto con el archivo de configuración especificado
mosquitto -c /mqtt-simulator/config/mosquitto.conf -v &

# Mostrar los logs de Mosquitto para verificar si está funcionando
tail -f /var/log/mosquitto/mosquitto.log
