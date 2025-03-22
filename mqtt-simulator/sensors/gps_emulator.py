#!/usr/bin/python 

import sys
import math
import requests
import json
import time
import paho.mqtt.client as mqtt
import random
import threading
from typing import List, Tuple

# Parte de la API OpenWeatherMap
base_url = 'http://api.openweathermap.org/data/2.5/weather'
api_key = '0ad1494d68c919961777dbf099dc8509'  # << Get your API key (APPID) here: http://openweathermap.org/appid

def get_temperature(lat: float, lon: float) -> dict:
    """Obtiene la temperatura para las coordenadas dadas"""
    query = base_url + '?lat=%s&lon=%s&units=metric&APPID=%s' % (lat, lon, api_key)
    try:
        response = requests.get(query)
        if response.status_code != 200:
            return {'error': 'N/A'}
        else:
            return response.json()
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)

def print_temperature_for_location(lat: float, lon: float) -> None:
    """Imprime la temperatura para una ubicación dada, incluyendo la ciudad"""
    location = get_temperature(lat, lon)
    if 'error' not in location:
        city_name = location.get('name', 'Desconocida')
        temperature = str(math.ceil(location['main']['temp']))
        print(f"Lat: {lat}, Lon: {lon} - {city_name} {temperature}°C ({location['main']['temp']}°C)")
    else:
        print(f"Lat: {lat}, Lon: {lon} - Error al obtener la temperatura.")

# Parte de simulación de GPS (Sensor Base y GPS Emulator)
class SensorBase:
    """Clase base para todos los sensores con funcionalidad común"""
    def __init__(self, config_file: str, topic_name: str):
        self.config = self._load_config(config_file)
        self.client = mqtt.Client()
        self.offline_file = "offline_data.json"
        self.topic = topic_name
        self.sensor_config = next(t["DATA"] for t in self.config["TOPICS"] if t.get("TOPIC_NAME") == topic_name)
    
    def _load_config(self, config_file: str) -> dict:
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            # Configuración predeterminada en caso de error
            return {
                "BROKER_URL": "localhost",
                "BROKER_PORT": 1883,
                "TOPICS": [{"TOPIC_NAME": "logix/gps", "DATA": {}}]
            }

    def connect_mqtt(self) -> bool:
        try:
            self.client.connect(self.config["BROKER_URL"], self.config["BROKER_PORT"])
            self.client.loop_start()
            print(f"Conectado a {self.config['BROKER_URL']}:{self.config['BROKER_PORT']}")
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

class GPSEmulator(SensorBase):
    def __init__(self, config_file: str, mapbox_token: str):
        super().__init__(config_file, "logix/gps")
        self.mapbox_token = mapbox_token
        self.current_route = []
        self.command_topic = "logix/gps/command"
        self.control_topic = "logix/gps/control"
        self.simulation_active = False
        self.simulation_thread = None
        self.stop_event = threading.Event()
        self.sensor_enabled = True  # Por defecto, el sensor está encendido
        
    def setup_listeners(self):
        """Configura los oyentes para comandos de ruta y control"""
        def on_command_message(client, userdata, msg):
            # Solo procesar comandos si el sensor está encendido
            if not self.sensor_enabled:
                print("Ignorando comando de ruta - Sensor apagado")
                return

            try:
                command_data = json.loads(msg.payload.decode())
                print(f"Comando recibido: {command_data}")
                
                start_lat = command_data.get("latinicio")
                start_lon = command_data.get("longinicio")
                end_lat = command_data.get("latdestino")
                end_lon = command_data.get("longdestino")
                
                # Valores predeterminados para steps e interval si no se proporcionan
                steps = command_data.get("steps", 10)
                interval = command_data.get("interval", 1.0)
                
                if all([start_lat, start_lon, end_lat, end_lon]):
                    # Detener simulación actual si está en ejecución
                    self.stop_current_simulation()
                    
                    print(f"Iniciando ruta desde ({start_lat}, {start_lon}) hasta ({end_lat}, {end_lon})")
                    print_temperature_for_location(start_lat, start_lon)
                    
                    self.generate_interpolated_route((start_lon, start_lat), (end_lon, end_lat), steps)
                    
                    # Iniciar nueva simulación en un hilo separado
                    self.stop_event.clear()
                    self.simulation_thread = threading.Thread(
                        target=self.simulate_journey, 
                        args=(interval,)
                    )
                    self.simulation_thread.daemon = True
                    self.simulation_thread.start()
                    self.simulation_active = True
                else:
                    print("Faltan parámetros en el comando")
                    
            except json.JSONDecodeError:
                print(f"Error al decodificar el comando JSON: {msg.payload}")
            except Exception as e:
                print(f"Error al procesar el comando: {e}")

        def on_control_message(client, userdata, msg):
            try:
                control_data = json.loads(msg.payload.decode())
                command = control_data.get("command", "").lower()
                
                if command == "off" or command == "apagar":
                    self.turn_off_sensor()
                elif command == "on" or command == "encender":
                    self.turn_on_sensor()
                else:
                    print(f"Comando de control desconocido: {command}")
                    
            except json.JSONDecodeError:
                print(f"Error al decodificar el comando de control: {msg.payload}")
            except Exception as e:
                print(f"Error al procesar el comando de control: {e}")
        
        # Configurar callback para mensajes en el topic de comandos de ruta
        self.client.message_callback_add(self.command_topic, on_command_message)
        
        # Configurar callback para mensajes en el topic de control
        self.client.message_callback_add(self.control_topic, on_control_message)
        
        # Callback por defecto para cualquier otro mensaje
        self.client.on_message = lambda client, userdata, msg: print(f"Mensaje recibido en topic {msg.topic}")
        
        # Suscribirse a los topics
        self.client.subscribe(self.command_topic)
        self.client.subscribe(self.control_topic)
        
        print(f"Suscrito al topic de comandos de ruta: {self.command_topic}")
        print(f"Suscrito al topic de control del sensor: {self.control_topic}")
        
    def turn_off_sensor(self):
        """Apaga el sensor de GPS"""
        if self.sensor_enabled:
            print("Apagando sensor de GPS...")
            self.sensor_enabled = False
            self.stop_current_simulation()
            # Publicar mensaje de estado del sensor
            status_msg = {"status": "off", "timestamp": time.time()}
            self.client.publish(f"{self.topic}/status", json.dumps(status_msg), qos=1)
            print("Sensor de GPS apagado")
            
    def turn_on_sensor(self):
        """Enciende el sensor de GPS"""
        if not self.sensor_enabled:
            print("Encendiendo sensor de GPS...")
            self.sensor_enabled = True
            # Publicar mensaje de estado del sensor
            status_msg = {"status": "on", "timestamp": time.time()}
            self.client.publish(f"{self.topic}/status", json.dumps(status_msg), qos=1)
            print("Sensor de GPS encendido y listo para recibir comandos")
    
    def stop_current_simulation(self):
        """Detiene la simulación actual si está en ejecución"""
        if self.simulation_active and self.simulation_thread and self.simulation_thread.is_alive():
            print("Deteniendo simulación actual...")
            self.stop_event.set()
            self.simulation_thread.join(timeout=2.0)  # Esperar hasta 2 segundos para que se detenga
            if self.simulation_thread.is_alive():
                print("La simulación no se detuvo limpiamente, continuando con nueva simulación")
            else:
                print("Simulación anterior detenida")
        self.simulation_active = False

    def get_route(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        start_lng, start_lat = start
        end_lng, end_lat = end

        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_lng},{start_lat};{end_lng},{end_lat}"
        params = {"access_token": self.mapbox_token, "geometries": "geojson", "overview": "full"}

        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                return data["routes"][0]["geometry"]["coordinates"]
            else:
                print("No se encontraron rutas en la respuesta")
                return []
        raise Exception(f"Error API Mapbox: {response.status_code}, {response.text}")

    def generate_interpolated_route(self, start: Tuple[float, float], end: Tuple[float, float], steps: int = 10) -> None:
        try:
            base_route = self.get_route(start, end)
            if base_route:
                self.current_route = self._interpolate_points(base_route, steps)
                print(f"Ruta generada con {len(self.current_route)} puntos")
            else:
                print("No se pudo generar la ruta: respuesta vacía de la API")
                self.current_route = []
        except Exception as e:
            print(f"Error al generar la ruta: {e}")
            self.current_route = []

    def _interpolate_points(self, coords: List[Tuple[float, float]], steps: int) -> List[Tuple[float, float]]:
        interpolated = []
        for i in range(len(coords) - 1):
            start = coords[i]
            end = coords[i + 1]
            for j in range(steps):
                ratio = j / steps
                lat = start[1] + (end[1] - start[1]) * ratio
                lon = start[0] + (end[0] - start[0]) * ratio
                interpolated.append((lon, lat))
        return interpolated

    def simulate_journey(self, interval: float):
        if not self.current_route:
            print("No hay ruta definida para simular")
            return
        
        print(f"Iniciando simulación con {len(self.current_route)} puntos...")
        
        for point in self.current_route:
            # Verificar si se solicitó detener la simulación o si el sensor está apagado
            if self.stop_event.is_set() or not self.sensor_enabled:
                reason = "solicitud de parada" if self.stop_event.is_set() else "sensor apagado"
                print(f"Simulación detenida por {reason}")
                break
                
            try:
                temperature_data = get_temperature(point[1], point[0])
                temperature = temperature_data['main']['temp'] if 'error' not in temperature_data and 'main' in temperature_data else None
                city_name = temperature_data.get('name', 'Desconocida')
                
                data = {
                    "lat": round(point[1], 6), 
                    "lon": round(point[0], 6), 
                    "temperature": temperature, 
                    "city": city_name
                }
                self.client.publish(self.topic, json.dumps(data), qos=2)
                print(f"Datos publicados: {data}")
                time.sleep(interval)
            except Exception as e:
                print(f"Error en la simulación: {e}")
                if self.stop_event.is_set() or not self.sensor_enabled:
                    break
        
        print("Simulación completada" if not self.stop_event.is_set() and self.sensor_enabled else "Simulación interrumpida")
        self.simulation_active = False

# Uso combinado
if __name__ == "__main__":
    # Configuración inicial
    CONFIG_PATH = "../../settings.json"
    MAPBOX_TOKEN = "pk.eyJ1IjoiZGF5a2V2MTIiLCJhIjoiY204MTd5NzR3MGdxYTJqcGlsa29odnQ5YiJ9.tbAEt453VxfJoDatpU72YQ"

    print("Iniciando GPS Emulator en modo automático...")
    print("Esperando comandos en el topic 'logix/gps/command'")
    print("Control de encendido/apagado en el topic 'logix/gps/control'")
    print("Comandos disponibles:")
    print(" - Ruta: mosquitto_pub -h localhost -t \"logix/gps/command\" -m '{\"latinicio\":19.432608,\"longinicio\":-99.133209,\"latdestino\":20.659698,\"longdestino\":-103.349609,\"steps\":10,\"interval\":1.0}'")
    print(" - Apagar: mosquitto_pub -h localhost -t \"logix/gps/control\" -m '{\"command\":\"off\"}'")
    print(" - Encender: mosquitto_pub -h localhost -t \"logix/gps/control\" -m '{\"command\":\"on\"}'")
    
    gps = GPSEmulator(CONFIG_PATH, MAPBOX_TOKEN)
    if gps.connect_mqtt():
        gps.setup_listeners()
        
        # Publicar estado inicial del sensor
        status_msg = {"status": "on", "timestamp": time.time()}
        gps.client.publish(f"{gps.topic}/status", json.dumps(status_msg), qos=1)
        
        # Mantener el programa en ejecución esperando comandos
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Programa finalizado por el usuario")
            gps.stop_current_simulation()
            gps.client.loop_stop()
    else:
        print("No se pudo iniciar el programa debido a errores de conexión")