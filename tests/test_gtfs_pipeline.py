"""Pruebas unitarias para el motor de datos GTFS oficial de Canarias."""

import pytest
from pathlib import Path
from src.data_ingestion.gtfs_loader import GTFSNetwork, detect_island, DB_PATH


def test_island_detection():
    assert detect_island(28.1068, -15.4172) == "Gran Canaria"
    assert detect_island(28.4682, -16.2444) == "Tenerife"
    assert detect_island(28.0908, -17.1085) == "La Gomera"
    assert detect_island(28.6755, -17.7663) == "La Palma"
    assert detect_island(28.0494, -14.3571) == "Fuerteventura"
    assert detect_island(28.8631, -13.8324) == "Lanzarote"


def test_gtfs_summary():
    engine = GTFSNetwork.get_instance()
    summary = engine.get_summary()
    assert summary["total_stops"] > 4000
    assert summary["total_routes"] > 200
    assert "TITSA" in summary["agencies"]
    assert "GUAGUAS" in summary["agencies"]
    assert "Tenerife" in summary["stops_by_island"]
    assert "Gran Canaria" in summary["stops_by_island"]


def test_gtfs_search():
    engine = GTFSNetwork.get_instance()
    # Búsqueda en Gran Canaria
    results_gc = engine.search_stops("Santa Catalina", island="Gran Canaria", limit=5)
    assert len(results_gc) > 0
    assert any("Santa Catalina" in r["name"] for r in results_gc)

    # Búsqueda en Tenerife
    results_tf = engine.search_stops("Santa Cruz", island="Tenerife", limit=5)
    assert len(results_tf) > 0


def test_gtfs_live_departures():
    engine = GTFSNetwork.get_instance()
    # Buscar una parada concurrida de Guaguas
    results = engine.search_stops("Santa Catalina", limit=1)
    assert len(results) > 0
    stop_id = results[0]["stop_id"]
    agency = results[0]["agency_id"]

    departures = engine.get_live_departures(stop_id=stop_id, agency_id=agency, limit=5)
    assert isinstance(departures, list)
    if departures:
        dep = departures[0]
        assert "line" in dep
        assert "arrival_window" in dep
        assert "crowding" in dep
        assert "expected_time" in dep
