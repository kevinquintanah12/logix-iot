#!/bin/bash

# Iniciar Mosquitto en segundo plano

pip install -r requirements.txt

# Iniciar los scripts Python (puedes agregar otros si los tienes)
python3 /mqtt-simulator/sensors/gps_emulator.py &
python3 /mqtt-simulator/sensors/iot_emulator.py &

# Esperar a que los procesos terminen (o mantener el contenedor activo)
wait
