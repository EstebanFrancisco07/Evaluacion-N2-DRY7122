import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_KEY")
if not MAPBOX_TOKEN:
    print("❌ No se encontró MAPBOX_KEY. Verifica tu archivo .env.")
    sys.exit(1)

GEOCODE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
DIRECTIONS_URL = "https://api.mapbox.com/directions/v5/mapbox/driving"
FUEL_L_POR_KM = 0.08

def geocode(ciudad: str):
    url = f"{GEOCODE_URL}/{ciudad}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "limit": 1,
        "language": "es"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data["features"]:
        raise ValueError(f"No se encontró la ciudad: {ciudad}")
    lon, lat = data["features"][0]["center"]
    return lat, lon

def obtener_ruta(origen: tuple, destino: tuple):
    url = f"{DIRECTIONS_URL}/{origen[1]},{origen[0]};{destino[1]},{destino[0]}"
    params = {
        "access_token": MAPBOX_TOKEN,
        "geometries": "geojson",
        "language": "es",
        "steps": "true"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def seg_a_hms(seg):
    h = int(seg // 3600)
    m = int((seg % 3600) // 60)
    s = int(seg % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def estimar_combustible(km, consumo=FUEL_L_POR_KM):
    return km * consumo

print("\n=== Evaluación Parcial Nº2 – Consumo con Mapbox ===")
print("Escribe 'q' para salir.\n")

while True:
    try:
        origen = input("Ciudad de Origen: ").strip()
        if origen.lower() == "q":
            break
        destino = input("Ciudad de Destino: ").strip()
        if destino.lower() == "q":
            break

        print("\n🔍 Geocodificando...")
        org = geocode(origen)
        dst = geocode(destino)

        print("🚗 Calculando ruta...")
        data = obtener_ruta(org, dst)
        route = data["routes"][0]
        dist_km = route["distance"] / 1000
        dur_sec = route["duration"]
        lit = estimar_combustible(dist_km)

        print(f"\n📏 Distancia : {dist_km:.2f} km")
        print(f"⏱  Duración  : {seg_a_hms(dur_sec)} (h:m:s)")
        print(f"⛽ Combustible: {lit:.2f} litros")

        print("\n🗺  Narrativa (ES):")
        for i, leg in enumerate(route["legs"][0]["steps"], 1):
            print(f" {i:02d}. {leg['maneuver']['instruction']}")

        print("\n---\n")

    except Exception as e:
        print("❌ Error:", e, "\n")