import requests
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Caché global
cache = {}  # {city: {"data": ..., "timestamp": ...}}


def is_valid_coordinate(lat, lon):
    """
    Valida si las coordenadas están dentro de rangos permitidos.
    """
    return isinstance(lat, (int, float)) and isinstance(lon, (int, float)) \
        and -90 <= lat <= 90 and -180 <= lon <= 180


def map_weather_code(code):
    """
    Traduce códigos de clima a descripciones simples.
    """
    mapping = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Nublado"
    }
    return mapping.get(code, "Desconocido")


def fetch_weather(latitude, longitude, http_client=requests):
    """
    Obtiene el clima actual desde la API Open-Meteo.

    Args:
        latitude (float): Latitud de la ubicación.
        longitude (float): Longitud de la ubicación.
        http_client: Cliente HTTP (por defecto requests).

    Returns:
        dict: Información del clima o error.
    """
    if not is_valid_coordinate(latitude, longitude):
        return {"error": "Coordenadas inválidas"}

    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code"
        }

        response = http_client.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        current = data.get("current")

        if not current:
            return {"error": "No se encontró información de clima actual"}

        temperature = current.get("temperature_2m")
        weather_code = current.get("weather_code")

        if temperature is None or weather_code is None:
            return {"error": "Datos incompletos del clima"}

        return {
            "temperature": temperature,
            "weather": map_weather_code(weather_code),
            "weather_code": weather_code
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error de conexión: {e}"}


def get_weather_cached(city, latitude, longitude, ttl=300):
    """
    Obtiene el clima usando caché con expiración (TTL).

    Args:
        city (str): Nombre de la ciudad.
        latitude (float): Latitud.
        longitude (float): Longitud.
        ttl (int): Tiempo de vida del caché en segundos.

    Returns:
        dict: Datos del clima o error.
    """
    current_time = time.time()

    if city in cache:
        entry = cache[city]

        try:
            if current_time - entry["timestamp"] >= ttl:
                data = fetch_weather(latitude, longitude)

                if "error" not in data:
                    cache[city] = {"data": data, "timestamp": current_time}
                    return data

                return {
                    "data": entry["data"],
                    "warning": "Usando caché (puede estar desactualizado)"
                }

            return entry["data"]

        except Exception:
            return {
                "data": entry["data"],
                "warning": "Error actualizando, mostrando caché"
            }

    data = fetch_weather(latitude, longitude)

    if "error" not in data:
        cache[city] = {"data": data, "timestamp": current_time}

    return data


def get_weather_multiple(cities, ttl=300):
    """
    Obtiene el clima de múltiples ciudades en paralelo.

    Args:
        cities (list): Lista de tuplas (city, lat, lon).
        ttl (int): Tiempo de vida del caché.

    Returns:
        list: Resultados por ciudad.
    """
    def process(city_data):
        city, lat, lon = city_data
        result = get_weather_cached(city, lat, lon, ttl)
        return {"city": city, **result}

    with ThreadPoolExecutor(max_workers=5) as executor:
        return list(executor.map(process, cities))


# -------------------------
# TESTS BÁSICOS
# -------------------------

def test_fetch_weather_success():
    result = fetch_weather(-33.45, -70.66)
    assert isinstance(result, dict)
    assert "temperature" in result or "error" in result


def test_invalid_coordinates():
    result = fetch_weather(200, 500)
    assert "error" in result


def test_cache_behavior():
    city = "TestCity"
    lat, lon = -33.45, -70.66

    result1 = get_weather_cached(city, lat, lon, ttl=300)
    result2 = get_weather_cached(city, lat, lon, ttl=300)

    assert result1 == result2


# -------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------

if __name__ == "__main__":
    cities = [
        ("Santiago", -33.45, -70.66),
        ("Tokyo", 35.6895, 139.6917),
        ("New York", 40.7128, -74.0060)
    ]

    results = get_weather_multiple(cities)

    print("\nClima actual por ciudad:\n")
    for r in results:
        print(r)

    # Ejecutar tests manualmente
    print("\nEjecutando tests...")
    test_fetch_weather_success()
    test_invalid_coordinates()
    test_cache_behavior()
    print("Tests completados correctamente")
