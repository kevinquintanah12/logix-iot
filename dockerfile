# Usar la imagen oficial de Mosquitto
FROM eclipse-mosquitto:latest

# Establecer el directorio de trabajo
WORKDIR /mqtt-simulator

# Crear el directorio donde se almacenarán los archivos de configuración
RUN mkdir -p config

# Copiar el archivo de configuración
COPY mqtt-simulator/config/mosquitto.conf /mqtt-simulator/config/mosquitto.conf

# Exponer los puertos necesarios (puedes cambiar el puerto si lo modificaste)
EXPOSE 1883
EXPOSE 9001

# Configurar el contenedor para usar el archivo de configuración
CMD ["mosquitto", "-c", "/mqtt-simulator/config/mosquitto.conf", "-v"]
