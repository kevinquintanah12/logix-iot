# Usa la imagen base de Mosquitto
FROM eclipse-mosquitto:latest

# Copia tu archivo de configuración desde tu máquina local al contenedor
COPY ./mqtt-simulator/config/mosquitto.conf /mosquitto/config/mosquitto.conf

# Expone los puertos que vas a usar
EXPOSE 1883 9001

# Comando por defecto para iniciar el contenedor
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
