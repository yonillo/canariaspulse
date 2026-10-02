"""Módulo de ingesta y modelado de la red de transporte interurbano (Global) de Gran Canaria.

Extrae paradas y rutas reales de OpenStreetMap (OSM) y genera registros operacionales
para alimentar los motores de inferencia clásica y bayesiana.
"""

from __future__ import annotations

import json
import logging
import math
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"


# Paradas clave y nodos neurálgicos de Gran Canaria (fallback / anclajes de alta fidelidad)
KEY_HUBS = [
    {"stop_id": "GC_STELMO", "name": "Estación de Guaguas San Telmo (Las Palmas)", "lat": 28.1068, "lon": -15.4172, "zone": "Capital", "altitude": 12, "is_hub": True},
    {"stop_id": "GC_SCATALINA", "name": "Intercambiador Santa Catalina (Las Palmas)", "lat": 28.1408, "lon": -15.4298, "zone": "Capital", "altitude": 8, "is_hub": True},
    {"stop_id": "GC_HOYA_PLATA", "name": "Hoya de la Plata (Salida Sur)", "lat": 28.0772, "lon": -15.4189, "zone": "Capital", "altitude": 35, "is_hub": False},
    {"stop_id": "GC_JINAMAR", "name": "Cruce de Jinámar (GC-1)", "lat": 28.0286, "lon": -15.4125, "zone": "Telde", "altitude": 45, "is_hub": False},
    {"stop_id": "GC_TELDE_EST", "name": "Estación de Guaguas de Telde", "lat": 27.9995, "lon": -15.4190, "zone": "Telde", "altitude": 130, "is_hub": True},
    {"stop_id": "GC_AEROPUERTO", "name": "Aeropuerto de Gran Canaria (Llegadas)", "lat": 27.9348, "lon": -15.3882, "zone": "Telde/Ingenio", "altitude": 24, "is_hub": True},
    {"stop_id": "GC_ARINAGA", "name": "Cruce de Arinaga (GC-1)", "lat": 27.8762, "lon": -15.4195, "zone": "Agüimes", "altitude": 75, "is_hub": False},
    {"stop_id": "GC_VECINDARIO", "name": "C.C. Atlántico / Vecindario", "lat": 27.8465, "lon": -15.4411, "zone": "Santa Lucía", "altitude": 55, "is_hub": True},
    {"stop_id": "GC_S_AGUSTIN", "name": "San Agustín (Clínica Roca)", "lat": 27.7695, "lon": -15.5392, "zone": "San Bartolomé", "altitude": 20, "is_hub": False},
    {"stop_id": "GC_PLAYA_INGLES", "name": "Playa del Inglés (Yumbo / Av. de Tirajana)", "lat": 27.7583, "lon": -15.5786, "zone": "San Bartolomé", "altitude": 30, "is_hub": True},
    {"stop_id": "GC_FARO_MASP", "name": "Estación Faro de Maspalomas", "lat": 27.7356, "lon": -15.5997, "zone": "San Bartolomé", "altitude": 5, "is_hub": True},
    {"stop_id": "GC_PUERTO_RICO", "name": "Estación de Puerto Rico", "lat": 27.7882, "lon": -15.7108, "zone": "Mogán", "altitude": 15, "is_hub": True},
    {"stop_id": "GC_MOGAN", "name": "Puerto de Mogán", "lat": 27.8188, "lon": -15.7644, "zone": "Mogán", "altitude": 3, "is_hub": True},
    # Medianías y Campus
    {"stop_id": "GC_TAFIRA_CAMPUS", "name": "Campus Universitario de Tafira (ULPGC)", "lat": 28.0722, "lon": -15.4542, "zone": "Universidad", "altitude": 275, "is_hub": True},
    {"stop_id": "GC_STA_BRIGIDA", "name": "Estación Santa Brígida", "lat": 28.0336, "lon": -15.5005, "zone": "Medianías", "altitude": 510, "is_hub": True},
    {"stop_id": "GC_SAN_MATEO", "name": "Estación Vega de San Mateo", "lat": 28.0094, "lon": -15.5322, "zone": "Medianías", "altitude": 840, "is_hub": True},
    # Norte
    {"stop_id": "GC_ARUCAS", "name": "Estación de Guaguas de Arucas", "lat": 28.1189, "lon": -15.5236, "zone": "Norte", "altitude": 240, "is_hub": True},
    {"stop_id": "GC_GALDAR", "name": "Estación de Guaguas de Gáldar", "lat": 28.1444, "lon": -15.6558, "zone": "Norte", "altitude": 120, "is_hub": True},
    {"stop_id": "GC_AGAETE", "name": "Puerto de Las Nieves (Agaete)", "lat": 28.1011, "lon": -15.7102, "zone": "Norte", "altitude": 10, "is_hub": True},
]

# Definición de las líneas troncales más emblemáticas de Global
ROUTES_CONFIG = [
    {
        "route_id": "L01",
        "route_short_name": "01",
        "route_long_name": "Las Palmas (San Telmo) - Puerto de Mogán",
        "corridor": "Sur - Costa",
        "stop_sequence": ["GC_STELMO", "GC_HOYA_PLATA", "GC_JINAMAR", "GC_AEROPUERTO", "GC_ARINAGA", "GC_VECINDARIO", "GC_S_AGUSTIN", "GC_PLAYA_INGLES", "GC_FARO_MASP", "GC_PUERTO_RICO", "GC_MOGAN"],
        "base_duration_min": 95,
        "nominal_headway_min": 20,
    },
    {
        "route_id": "L30",
        "route_short_name": "30",
        "route_long_name": "Santa Catalina / San Telmo - Faro de Maspalomas (Directo)",
        "corridor": "Sur - Exprés Turístico",
        "stop_sequence": ["GC_SCATALINA", "GC_STELMO", "GC_HOYA_PLATA", "GC_AEROPUERTO", "GC_S_AGUSTIN", "GC_PLAYA_INGLES", "GC_FARO_MASP"],
        "base_duration_min": 55,
        "nominal_headway_min": 15,
    },
    {
        "route_id": "L50",
        "route_short_name": "50",
        "route_long_name": "Las Palmas (San Telmo) - Faro de Maspalomas (Por Autopista)",
        "corridor": "Sur - Directo",
        "stop_sequence": ["GC_STELMO", "GC_HOYA_PLATA", "GC_FARO_MASP"],
        "base_duration_min": 45,
        "nominal_headway_min": 30,
    },
    {
        "route_id": "L91",
        "route_short_name": "91",
        "route_long_name": "Las Palmas (San Telmo) - Puerto Rico / Mogán (Directo)",
        "corridor": "Sur - Exprés Autovía",
        "stop_sequence": ["GC_STELMO", "GC_AEROPUERTO", "GC_PUERTO_RICO", "GC_MOGAN"],
        "base_duration_min": 60,
        "nominal_headway_min": 60,
    },
    {
        "route_id": "L303",
        "route_short_name": "303",
        "route_long_name": "Las Palmas (San Telmo) - Santa Brígida - San Mateo",
        "corridor": "Centro - Medianías",
        "stop_sequence": ["GC_STELMO", "GC_TAFIRA_CAMPUS", "GC_STA_BRIGIDA", "GC_SAN_MATEO"],
        "base_duration_min": 48,
        "nominal_headway_min": 20,
    },
    {
        "route_id": "L103",
        "route_short_name": "103",
        "route_long_name": "Las Palmas (San Telmo) - Gáldar - Agaete (Puerto)",
        "corridor": "Norte - GC-2",
        "stop_sequence": ["GC_STELMO", "GC_ARUCAS", "GC_GALDAR", "GC_AGAETE"],
        "base_duration_min": 52,
        "nominal_headway_min": 30,
    },
    {
        "route_id": "L12",
        "route_short_name": "12",
        "route_long_name": "Las Palmas (San Telmo) - Telde",
        "corridor": "Sureste - Interurbano",
        "stop_sequence": ["GC_STELMO", "GC_HOYA_PLATA", "GC_JINAMAR", "GC_TELDE_EST"],
        "base_duration_min": 28,
        "nominal_headway_min": 10,
    }
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia geodésica ortodrómica en kilómetros entre dos coordenadas."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.asin(math.sqrt(a))


def fetch_osm_bus_stops(cache: bool = True) -> pd.DataFrame:
    """Descarga o carga de caché las paradas de guaguas en Gran Canaria desde OpenStreetMap."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = RAW_DATA_DIR / "gran_canaria_stops_osm.json"

    if cache and cache_file.exists():
        logger.info("Cargando paradas de Gran Canaria desde caché local: %s", cache_file)
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        logger.info("Consultando Overpass API para obtener paradas de Gran Canaria...")
        query = """
        [out:json][timeout:35];
        area['name'='Gran Canaria']->.searchArea;
        (
          node['highway'='bus_stop'](area.searchArea);
        );
        out body;
        """
        encoded_data = urllib.parse.urlencode({"data": query}).encode("utf-8")
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=encoded_data,
            headers={"User-Agent": "GlobalPulse-ULPGC-Research/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            logger.info("Descarga completada y guardada en caché: %d elementos", len(data.get("elements", [])))
        except Exception as e:
            logger.warning("Fallo al consultar Overpass API (%s). Usando red base de alta fidelidad.", e)
            return pd.DataFrame(KEY_HUBS)

    elements = data.get("elements", [])
    records = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("description") or f"Parada {el['id']}"
        ref = tags.get("ref", str(el["id"]))
        records.append({
            "stop_id": f"OSM_{el['id']}",
            "stop_code": ref,
            "name": name,
            "lat": el["lat"],
            "lon": el["lon"],
            "zone": tags.get("addr:city") or "Gran Canaria",
            "operator": tags.get("operator", "Global"),
            "shelter": tags.get("shelter") == "yes",
            "bench": tags.get("bench") == "yes",
        })

    df = pd.DataFrame(records)
    # Deduplicar o limpiar coordenadas que caigan fuera del bounding box de Gran Canaria
    # Gran Canaria aprox: lat [27.70, 28.25], lon [-15.90, -15.35]
    df = df[(df["lat"] >= 27.70) & (df["lat"] <= 28.25) & (df["lon"] >= -15.90) & (df["lon"] <= -15.35)]
    logger.info("Total de paradas válidas procesadas: %d", len(df))
    return df


def get_curated_network() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna los DataFrames de las paradas troncales y las rutas principales configuradas."""
    stops_df = pd.DataFrame(KEY_HUBS)
    routes_df = pd.DataFrame(ROUTES_CONFIG)
    return stops_df, routes_df


def generate_operational_telemetry(
    num_days: int = 45,
    seed: int = 42
) -> pd.DataFrame:
    """Genera datos empíricos de operaciones y viajes de guaguas con física y factores reales.

    Incluye:
    - Retrasos que siguen una distribución Log-Normal o Weibull según tráfico.
    - Factor de hora punta (mañana 7-9h, mediodía 13:30-15h, tarde 18-20h).
    - Factor de día de la semana (Laborable vs Fin de Semana).
    - Factor meteorológico: Alertas de lluvia en medianías o viento/calima en el sureste.
    - Incidencias aleatorias de tráfico en la autopista GC-1 (atascos reales en Jinámar/Hoya de la Plata).
    """
    np.random.seed(seed)
    stops_dict = {s["stop_id"]: s for s in KEY_HUBS}
    records = []

    # Fechas simuladas recientes
    start_date = pd.Timestamp("2026-08-15")

    for day_idx in range(num_days):
        current_date = start_date + pd.Timedelta(days=day_idx)
        is_weekend = current_date.weekday() >= 5
        day_name = current_date.day_name()

        # Condición meteorológica del día: normal (80%), lluvia_medianias (12%), calima_viento (8%)
        weather_roll = np.random.rand()
        if weather_roll < 0.12:
            weather = "Lluvia Medianias"
        elif weather_roll < 0.20:
            weather = "Calima/Viento"
        else:
            weather = "Despejado/Normal"

        # Incidencia de colapso en GC-1 (atasco grave por accidente o aforo excesivo): 10% días
        gc1_incident = np.random.rand() < 0.10

        for route in ROUTES_CONFIG:
            route_id = route["route_id"]
            corridor = route["corridor"]
            base_duration = route["base_duration_min"]
            nominal_headway = route["nominal_headway_min"]
            stops_seq = route["stop_sequence"]

            # Distancia total de la ruta sumando tramos
            total_dist_km = 0.0
            for i in range(len(stops_seq) - 1):
                s1 = stops_dict[stops_seq[i]]
                s2 = stops_dict[stops_seq[i + 1]]
                total_dist_km += haversine_km(s1["lat"], s1["lon"], s2["lat"], s2["lon"])

            # Desnivel acumulado positivo
            elev_gain = sum(
                max(0, stops_dict[stops_seq[i + 1]]["altitude"] - stops_dict[stops_seq[i]]["altitude"])
                for i in range(len(stops_seq) - 1)
            )

            # Expediciones a lo largo del día (de 06:00 a 23:00)
            daily_trips = int(17 * 60 / (nominal_headway * (1.3 if is_weekend else 1.0)))

            # Horas de salida
            departure_minutes = np.linspace(6 * 60, 23 * 60, daily_trips)

            for dep_min in departure_minutes:
                hour = int(dep_min // 60)
                minute = int(dep_min % 60)
                sched_dep = current_date.replace(hour=hour, minute=minute, second=0)

                # Factor de hora punta (GC-1 y Tafira se saturan a las 07:30-09:00 y 14:00-15:30)
                is_morning_peak = 7 <= hour <= 9
                is_afternoon_peak = 14 <= hour <= 16
                is_peak = is_morning_peak or is_afternoon_peak

                peak_multiplier = 1.0
                if is_peak:
                    peak_multiplier = 1.25 if not is_weekend else 1.05

                # Efecto meteorológico
                weather_delay_factor = 1.0
                if weather == "Lluvia Medianias" and "Medianías" in corridor:
                    weather_delay_factor = 1.30
                elif weather == "Calima/Viento" and "Sur" in corridor:
                    weather_delay_factor = 1.10

                # Efecto GC-1 incidente
                incident_delay = 0.0
                if gc1_incident and "Sur" in corridor and 7 <= hour <= 19:
                    # Retraso grave con distribución Weibull (cola pesada)
                    incident_delay = float(np.random.weibull(a=1.8) * 15.0)

                # Generación de duración real mediante distribución Log-Normal
                # log(T) ~ N(mu, sigma)
                target_mean_duration = base_duration * peak_multiplier * weather_delay_factor + incident_delay
                sigma_trip = 0.12 if not is_weekend else 0.08
                if "Medianías" in corridor:
                    sigma_trip += 0.04

                mu_trip = np.log(target_mean_duration) - (sigma_trip ** 2) / 2.0
                actual_duration = float(np.random.lognormal(mean=mu_trip, sigma=sigma_trip))

                # Retraso (minutos) respecto a lo programado
                delay_min = actual_duration - base_duration
                # Categoría de puntualidad (Ontime si delay <= 3 min, Leve si <= 8 min, Grave > 8 min)
                if delay_min <= 3.0:
                    status = "A tiempo"
                elif delay_min <= 8.0:
                    status = "Retraso leve"
                else:
                    status = "Retraso severo"

                # Proceso de Poisson para afluencia de pasajeros en esa expedición
                base_passengers = 35 if "Sur" in corridor or "Medianías" in corridor else 25
                lambda_passengers = base_passengers * (1.4 if is_peak else 0.8)
                if is_weekend and "Exprés Turístico" in corridor:
                    lambda_passengers *= 1.3
                actual_passengers = int(np.random.poisson(lam=max(5, lambda_passengers)))
                actual_passengers = min(actual_passengers, 65)  # Capacidad máxima de una guagua interurbana

                records.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "scheduled_departure": sched_dep.strftime("%Y-%m-%d %H:%M"),
                    "hour": hour,
                    "day_of_week": day_name,
                    "is_weekend": int(is_weekend),
                    "is_peak": int(is_peak),
                    "route_id": route_id,
                    "route_short_name": route["route_short_name"],
                    "corridor": corridor,
                    "distance_km": round(total_dist_km, 2),
                    "elevation_gain_m": elev_gain,
                    "weather": weather,
                    "gc1_incident": int(gc1_incident and "Sur" in corridor),
                    "scheduled_duration_min": base_duration,
                    "actual_duration_min": round(actual_duration, 2),
                    "delay_min": round(delay_min, 2),
                    "status": status,
                    "passengers_onboard": actual_passengers,
                    "capacity": 65,
                    "occupancy_rate": round(actual_passengers / 65.0, 3),
                })

    df_telemetry = pd.DataFrame(records)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DATA_DIR / "telemetry_operations.parquet"
    df_telemetry.to_parquet(out_path, index=False)
    csv_path = PROCESSED_DATA_DIR / "telemetry_operations.csv"
    df_telemetry.to_csv(csv_path, index=False)
    logger.info("Telemetría operacional generada con éxito: %d expediciones registradas", len(df_telemetry))
    return df_telemetry


if __name__ == "__main__":
    print("Iniciando extracción y generación de datos para Global Gran Canaria...")
    osm_stops = fetch_osm_bus_stops(cache=True)
    stops_curated, routes_curated = get_curated_network()
    telemetry = generate_operational_telemetry(num_days=45)
    print(f"Resumen generado: {len(telemetry)} expediciones guardadas en {PROCESSED_DATA_DIR}")
