import subprocess
import os

MOSQUITTO_CONFIG_PATH = "config/mosquitto.conf"

def start_broker():
    """Inicia el broker Mosquitto con la configuración personalizada."""
    try:
        print("Iniciando broker MQTT...")
        subprocess.run(["mosquitto", "-c", MOSQUITTO_CONFIG_PATH], check=True)
    except Exception as e:
        print(f"Error iniciando el broker: {e}")

if __name__ == "__main__":
    start_broker()

