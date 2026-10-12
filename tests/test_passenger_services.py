"""Batería de pruebas formales para servicios al pasajero y cálculo garantizado de salida."""

from __future__ import annotations

import pytest
from datetime import datetime
from src.passenger_services import (
    calculate_guaranteed_departure_time,
    plan_multimodal_trip,
    get_live_departures_for_hub,
    resolve_hub_details,
    estimate_hub_to_hub_duration,
)


def test_resolve_hub_details():
    """Valida la resolución canónica de identificadores y alias insulares."""
    h_stelmo = resolve_hub_details("SAN_TELMO")
    assert h_stelmo["stop_id"] == "GC_STELMO"

    h_tafira = resolve_hub_details("CAMPUS_TAFIRA")
    assert h_tafira["stop_id"] == "GC_TAFIRA_CAMPUS"

    h_aero = resolve_hub_details("GC_AEROPUERTO")
    assert "Aeropuerto" in h_aero["name"]


def test_estimate_hub_to_hub_duration():
    """Valida que los tiempos de viaje sean consistentes con la orografía insular."""
    h_stelmo = resolve_hub_details("GC_STELMO")
    h_tafira = resolve_hub_details("GC_TAFIRA_CAMPUS")
    h_masp = resolve_hub_details("GC_FARO_MASP")

    dur_tafira = estimate_hub_to_hub_duration(h_stelmo, h_tafira)
    dur_masp = estimate_hub_to_hub_duration(h_stelmo, h_masp)

    # San Telmo a Campus Tafira (~16-25 min)
    assert 12 <= dur_tafira <= 30
    # San Telmo a Maspalomas (~40-60 min)
    assert 35 <= dur_masp <= 65
    assert dur_masp > dur_tafira


def test_calculate_guaranteed_departure_time():
    """Valida el cálculo analítico del cuantil bayesiano 95% (HDI)."""
    # Escenario normal
    res_normal = calculate_guaranteed_departure_time(
        origin_id="SAN_TELMO",
        destination_id="CAMPUS_TAFIRA",
        target_arrival_time="08:30",
        is_peak=False,
        incident_gc1=False,
        walk_buffer_min=5,
    )
    assert "recommended_departure" in res_normal
    assert res_normal["confidence_level"] == "95% (Intervalo Bayesiano HDI)"
    assert res_normal["expected_travel_time_mean"] > 0
    assert res_normal["safety_margin_min"] > 0

    # Escenario con hora punta e incidente en GC-1
    res_congested = calculate_guaranteed_departure_time(
        origin_id="SAN_TELMO",
        destination_id="CAMPUS_TAFIRA",
        target_arrival_time="08:30",
        is_peak=True,
        incident_gc1=True,
        walk_buffer_min=5,
    )
    # En escenario congestionado, la antelación requerida debe ser estrictamente mayor
    assert res_congested["total_buffer_minutes"] > res_normal["total_buffer_minutes"]
    assert res_congested["safety_margin_min"] > res_normal["safety_margin_min"]


def test_plan_multimodal_trip():
    """Valida la generación de las 3 alternativas con itinerarios y pasos desglosados."""
    plans = plan_multimodal_trip(
        origin_id="SAN_TELMO",
        destination_id="CAMPUS_TAFIRA",
        target_arrival_time="08:30",
        is_peak=True,
        incident_gc1=False,
        walk_buffer_min=5,
    )
    assert len(plans) == 3
    for p in plans:
        assert "id" in p
        assert "title" in p
        assert "departure_time" in p
        assert "arrival_time" in p
        assert len(p["steps"]) >= 4


def test_multimodal_maritime_trip():
    """Valida la generación de la ruta multimodal combinada Guagua + Ferry Fred. Olsen a Tenerife."""
    plans = plan_multimodal_trip(
        origin_id="CAMPUS_TAFIRA",
        destination_id="TENERIFE_SANTA_CRUZ",
        target_arrival_time="18:00",
        is_peak=True,
        incident_gc1=False,
        walk_buffer_min=5,
    )
    assert len(plans) == 3
    assert "Fred. Olsen" in plans[0]["title"] or "Bajamar Express" in plans[0]["title"]
    assert any("Agaete" in step["text"] for step in plans[0]["steps"])

    # Validar cálculo de salida garantizada para enlace marítimo
    dep = calculate_guaranteed_departure_time(
        origin_id="CAMPUS_TAFIRA",
        destination_id="TENERIFE_SANTA_CRUZ",
        target_arrival_time="18:00",
    )
    assert dep["total_buffer_minutes"] >= 120
    assert "95%" in dep["confidence_level"]


def test_titsa_and_balearia_services():
    """Valida la resolución y enrutamiento multimodal para TITSA, Baleària y Tranvía de Tenerife."""
    # Test resolución de hubs en Tenerife
    h_sc = resolve_hub_details("INTERCAMBIADOR_SANTA_CRUZ")
    assert "Santa Cruz" in h_sc["name"]
    h_ll = resolve_hub_details("INTERCAMBIADOR_LA_LAGUNA")
    assert "La Laguna" in h_ll["name"]

    # Test planificación interna en Tenerife (TITSA / Tranvía)
    titsa_plans = plan_multimodal_trip(
        origin_id="INTERCAMBIADOR_SANTA_CRUZ",
        destination_id="INTERCAMBIADOR_LA_LAGUNA",
        target_arrival_time="09:00",
    )
    assert len(titsa_plans) == 3
    assert any("TITSA" in p["title"] for p in titsa_plans)

    # Test presencia de opción Baleària en trayecto interinsular
    inter_plans = plan_multimodal_trip(
        origin_id="TERMINAL_BALEARIA_LPA",
        destination_id="INTERCAMBIADOR_SANTA_CRUZ",
        target_arrival_time="17:00",
    )
    assert any("Baleària" in p["title"] for p in inter_plans)


