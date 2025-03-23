import subprocess
import os

MOSQUITTO_CONFIG_PATH = "../config/mosquitto.conf"


def check_broker_config():
    """Verifica que los parámetros clave de Mosquitto sean adecuados."""
    required_params = {
        "persistence": "true",  # Asegura la persistencia de mensajes
        "persistence_location": "/var/lib/mosquitto/",
        "allow_anonymous": "true",  # Permitir conexiones anónimas (ajustable)
        "listener": "1885",  # Puerto estándar MQTT
        "max_queued_messages": "1000",  # Control de carga dinámica
        "message_size_limit": "262144",  # Límite de tamaño de mensaje (256 KB)
        "retry_interval": "10",  # Reintento de conexión en segundos
        "max_inflight_messages": "50"  # Mensajes en vuelo permitidos
    }

    try:
        if not os.path.exists(MOSQUITTO_CONFIG_PATH):
            print(f"Error: No se encontró {MOSQUITTO_CONFIG_PATH}")
            return False

        with open(MOSQUITTO_CONFIG_PATH, "r") as config_file:
            config_lines = config_file.readlines()

        config_dict = {line.split()[0]: line.split()[1] for line in config_lines if line.strip() and not line.startswith("#")}

        for param, expected_value in required_params.items():
            if param in config_dict:
                if config_dict[param] != expected_value:
                    print(f"Advertencia: {param} debería ser {expected_value}, pero se encontró {config_dict[param]}")
            else:
                print(f"Advertencia: Falta {param} en la configuración.")

        return True
    except Exception as e:
        print(f"Error al verificar la configuración: {e}")
        return False

def start_broker():
    """Inicia el broker Mosquitto si la configuración es correcta."""
    if check_broker_config():
        try:
            print("Iniciando broker MQTT con configuración validada...")
            subprocess.run(["mosquitto", "-c", MOSQUITTO_CONFIG_PATH], check=True)
        except Exception as e:
            print(f"Error iniciando el broker: {e}")
    else:
        print("No se inició Mosquitto debido a configuraciones incorrectas.")

if __name__ == "__main__":
    start_broker()
