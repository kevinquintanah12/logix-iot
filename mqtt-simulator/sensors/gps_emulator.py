import json
import time
import paho.mqtt.client as mqtt
import random
import requests
from typing import List, Tuple

class SensorBase:
    """Clase base para todos los sensores con funcionalidad común"""
    def __init__(self, config_file: str, topic_name: str):
        self.config = self._load_config(config_file)
        self.client = mqtt.Client()
        self.offline_file = "offline_data.json"
        self.topic = next(t["TOPIC_NAME"] for t in self.config["TOPICS"] if t.get("TOPIC_NAME") == topic_name)
        self.sensor_config = next(t["DATA"] for t in self.config["TOPICS"] if t.get("TOPIC_NAME") == topic_name)
        
    def _load_config(self, config_file: str) -> dict:
        with open(config_file) as f:
            return json.load(f)
    
    def connect_mqtt(self) -> bool:
        try:
            self.client.connect(
                self.config["BROKER_URL"],
                self.config["BROKER_PORT"]
            )
            self.client.loop_start()  # Iniciar el loop de MQTT
            print(f"Conectado a {self.config['BROKER_URL']}:{self.config['BROKER_PORT']}")
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def _handle_offline_data(self, data: dict):
        """Manejo unificado de datos offline"""
        try:
            with open(self.offline_file, "a") as f:
                json.dump(data, f)
                f.write("\n")
            print("Datos guardados en modo offline")
        except Exception as e:
            print(f"Error al guardar offline: {e}")

class GPSEmulator(SensorBase):
    def __init__(self, config_file: str, mapbox_token: str):
        super().__init__(config_file, "logix/gps")
        self.mapbox_token = mapbox_token
        self.current_route = []
        self.current_position = self._get_initial_position()
        self.offline_data = self._load_offline_data()  # Cargar datos offline
        
    def _get_initial_position(self) -> dict:
        """Obtiene posición inicial desde la configuración"""
        return {
            "lat": random.uniform(
                next(f["RANGE_START"] for f in self.sensor_config if f["NAME"] == "lat"),
                next(f["RANGE_END"] for f in self.sensor_config if f["NAME"] == "lat")
            ),
            "lon": random.uniform(
                next(f["RANGE_START"] for f in self.sensor_config if f["NAME"] == "lon"),
                next(f["RANGE_END"] for f in self.sensor_config if f["NAME"] == "lon")
            )
        }
    
    def _load_offline_data(self) -> List[dict]:
        """Carga datos almacenados en modo offline"""
        try:
            with open(self.offline_file, "r") as f:
                return [json.loads(line) for line in f]
        except FileNotFoundError:
            return []
    
    def get_route(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Obtiene ruta completa desde Mapbox Directions API"""
        start_lng, start_lat = start
        end_lng, end_lat = end

        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_lng},{start_lat};{end_lng},{end_lat}"

        params = {
            "access_token": self.mapbox_token,
            "geometries": "geojson",
            "overview": "full"
        }

        print("URL:", url)  # Debugging: Verifica la URL generada

        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()["routes"][0]["geometry"]["coordinates"]
        
        raise Exception(f"Error API Mapbox: {response.status_code}, {response.text}")
    

    def generate_interpolated_route(self, start: Tuple[float, float], end: Tuple[float, float], steps: int = 10) -> None:
        """Genera ruta interpolada para movimiento suave"""
        base_route = self.get_route(start, end)
        self.current_route = self._interpolate_points(base_route, steps)
    
    def _interpolate_points(self, coords: List[Tuple[float, float]], steps: int) -> List[Tuple[float, float]]:
        """Interpola puntos en la ruta"""
        if len(coords) < 2:
            raise ValueError("Necesitas al menos dos puntos para interpolar")
        
        interpolated = []
        for i in range(len(coords)-1):
            start = coords[i]
            end = coords[i+1]
            for j in range(steps):
                ratio = j / steps
                lat = start[1] + (end[1] - start[1]) * ratio
                lon = start[0] + (end[0] - start[0]) * ratio
                interpolated.append((lon, lat))
        return interpolated
    
    def simulate_journey(self):
        """Simula el recorrido completo con capacidad offline"""
        try:
            if not self.connect_mqtt():
                raise ConnectionError("No se pudo conectar al broker MQTT")
            
            # Enviar datos offline pendientes
            for data in self.offline_data:
                try:
                    self.client.publish(self.topic, json.dumps(data), qos=2)
                    print(f"Datos offline enviados: {data}")
                except Exception as e:
                    print(f"Error al enviar datos offline: {e}")
            
            if self.current_route:
                for point in self.current_route:
                    data = {
                        "lat": round(point[1], 6),
                        "lon": round(point[0], 6),
                        "speed": random.randint(
                            next(f["RANGE_START"] for f in self.sensor_config if f["NAME"] == "speed"),
                            next(f["RANGE_END"] for f in self.sensor_config if f["NAME"] == "speed")
                        )
                    }
                    try:
                        self.client.publish(self.topic, json.dumps(data), qos=2)
                        print(f"Datos publicados: {data}")
                    except Exception as e:
                        self._handle_offline_data(data)
                    
                    time.sleep(next(t["TIME_INTERVAL"] for t in self.config["TOPICS"] if t.get("TOPIC_NAME") == "logix/gps"))
            else:
                print("No hay ruta generada")
        
        except Exception as e:
            print(f"Error en simulación: {e}")
        finally:
            self.client.disconnect()

# Uso mejorado
if __name__ == "__main__":
    # Configuración inicial
    CONFIG_PATH = "../../settings.json"
    MAPBOX_TOKEN = "pk.eyJ1IjoiZGF5a2V2MTIiLCJhIjoiY204MTd5NzR3MGdxYTJqcGlsa29odnQ5YiJ9.tbAEt453VxfJoDatpU72YQ"
    START_POINT = (-97.02837490778721, 18.915445449596163)
    END_POINT = (-97.07341430889971, 18.858065728384958)
    
    # Inicializar y ejecutar
    gps = GPSEmulator(CONFIG_PATH, MAPBOX_TOKEN)
    gps.generate_interpolated_route(START_POINT, END_POINT, steps=20)
    gps.simulate_journey()

#si ves esto envia ayuda