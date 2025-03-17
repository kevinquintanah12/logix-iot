import json
import time
import paho.mqtt.client as mqtt
import random

class GPSEmulator:
    def __init__(self, config_file="../../settings.json"):
        with open(config_file) as f:
            self.config = json.load(f)
            
        self.client = mqtt.Client()
        self.gps_config = next(
            t for t in self.config["TOPICS"] if t.get("TOPIC_NAME") == "logix/gps"
        )

    def _generate_gps_data(self):
        return {
            field["NAME"]: self._generate_value(field)
            for field in self.gps_config["DATA"]
        }

    def _generate_value(self, field_config):
        if field_config["TYPE"] == "float":
            return round(random.uniform(field_config["RANGE_START"], field_config["RANGE_END"]), 6)
        elif field_config["TYPE"] == "int":
            return random.randint(field_config["RANGE_START"], field_config["RANGE_END"])
            
    def start_simulation(self):
        try:
            self.client.connect(
                self.config["BROKER_URL"],
                self.config["BROKER_PORT"]
            )
            print(f"Conectado al broker MQTT en {self.config['BROKER_URL']}:{self.config['BROKER_PORT']}")
        except Exception as e:
            print(f"Error al conectar con el broker MQTT: {e}")
            return
        
        while True:
            data = self._generate_gps_data()
            try:
                self.client.publish(
                    self.gps_config["TOPIC_NAME"],
                    json.dumps(data),
                    qos=2
                )
                print(f"Datos publicados en {self.gps_config['TOPIC_NAME']}: {data}")
            except Exception as e:
                print(f"Error al publicar mensaje: {e}")
            
            time.sleep(self.gps_config.get("TIME_INTERVAL", 10))  # Valor por defecto si no está definido

# Ejemplo de uso
if __name__ == "__main__":
    emulator = GPSEmulator()
    emulator.start_simulation()