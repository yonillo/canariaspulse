"""FastAPI Backend Server para Global Móvil 2.0 (Gran Canaria Smart Transit).

Expone todos los modelos matemáticos, algoritmos de inferencia y optimización,
telemetría en vivo y servicios al pasajero mediante endpoints RESTful de alta velocidad.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from src.data_ingestion.extract_network import KEY_HUBS
from src.data_ingestion.network_data import (
    HIGHWAY_POLYLINES,
    OFFICIAL_STOPS,
    TICKET_OFFICES,
    get_live_simulated_fleet,
    search_stop_by_code,
)
from src.data_ingestion.multimodal_data import (
    OPERATORS,
    MULTIMODAL_HUBS,
    MULTIMODAL_LINES,
    get_live_multimodal_fleet,
)
from src.passenger_services import (
    calculate_free_transit_progress,
    calculate_guaranteed_departure_time,
    generate_virtual_card_qr,
    get_live_departures_for_hub,
    get_live_service_alerts,
    get_network_lines_catalog,
    plan_multimodal_trip,
)
from src.bayesian.bayesian_network import GranCanariaBayesianNetwork
from src.core_stats.linear_regression import fit_travel_time_ols
from src.optimization import (
    solve_fleet_dispatch_milp,
    optimize_bpr_gradient_descent,
    optimize_bpr_newton,
    solve_lagrangian_frequency_allocation,
    solve_tsp_simulated_annealing,
    solve_tsp_genetic_algorithm,
)

from src.data_ingestion.gtfs_loader import (
    gtfs_engine,
    download_official_feeds,
    build_unified_database,
)

app = FastAPI(
    title="Global Móvil 2.0 / Canarias MaaS API",
    description="Motor de Inferencia Estadística, Modelos Bayesianos, GTFS Oficial y Optimización Operativa para Canarias",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache de modelos
_bayesian_net = None
_ols_bundle = None

def get_bayesian_net() -> GranCanariaBayesianNetwork:
    global _bayesian_net
    if _bayesian_net is None:
        _bayesian_net = GranCanariaBayesianNetwork()
    return _bayesian_net

def get_ols_bundle():
    global _ols_bundle
    if _ols_bundle is None:
        parquet_path = ROOT_DIR / "data" / "processed" / "telemetry_operations.parquet"
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
            bundle, _ = fit_travel_time_ols(df)
            _ols_bundle = bundle
    return _ols_bundle


# Modelos de entrada Pydantic
class RoutePlanRequest(BaseModel):
    origin_id: str = "SAN_TELMO"
    destination_id: str = "CAMPUS_TAFIRA"
    is_peak: bool = True
    incident_gc1: bool = False
    target_arrival_time: str = "08:30"
    walk_buffer_min: int = 5

class CausalSimRequest(BaseModel):
    incident_gc1: bool = False
    is_peak: bool = True
    rain_medianias: bool = False

class OptimizationRequest(BaseModel):
    problem: str = "milp"  # milp, newton, lagrange, tsp_sa, tsp_ga
    bus_budget: int = 25
    driver_hours: float = 60.0


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Global Móvil 2.0 API",
        "timestamp": datetime.now().isoformat(),
        "total_stops": len(OFFICIAL_STOPS),
    }


@app.get("/api/network/overview")
def get_network_overview():
    normalized_stops = []
    for s in OFFICIAL_STOPS:
        item = dict(s)
        item["code"] = s.get("stop_code", "")
        item["locality"] = s.get("zone", "Gran Canaria")
        item["id"] = s.get("stop_code", "")
        normalized_stops.append(item)

    # Combinar hubs insulares con terminales marítimas y urbanas
    hubs_map = {}
    for h in KEY_HUBS:
        hubs_map[h["stop_id"]] = h
    for k, v in MULTIMODAL_HUBS.items():
        hubs_map[k] = v
        # Integrar los hubs de Tenerife y terminales marítimas a paradas visibles en mapa
        if not any(s.get("id") == k or s.get("code") == v.get("stop_id") for s in normalized_stops):
            normalized_stops.append({
                "id": k,
                "code": v.get("stop_id", k),
                "name": v.get("name", k),
                "locality": v.get("locality", "Canarias"),
                "lat": v.get("lat"),
                "lon": v.get("lon"),
                "is_hub": True,
                "operators": v.get("operators", []),
            })

    # Combinar catálogo de líneas (Global + TITSA + Baleària + Fred Olsen + Armas + Guaguas Muni + Tranvía)
    combined_lines = list(MULTIMODAL_LINES)
    existing_line_ids = {l.get("line_id", l.get("short_name", "")) for l in combined_lines}
    for gl in get_network_lines_catalog():
        gl_id = gl.get("line_id", gl.get("line", ""))
        if gl_id not in existing_line_ids:
            gl_copy = dict(gl)
            gl_copy["line_id"] = gl_id
            combined_lines.append(gl_copy)

    return {
        "operators": OPERATORS,
        "hubs": hubs_map,
        "official_stops": normalized_stops,
        "ticket_offices": TICKET_OFFICES,
        "highway_polylines": HIGHWAY_POLYLINES,
        "lines_catalog": combined_lines,
        "gtfs_summary": gtfs_engine.get_summary(),
    }


@app.get("/api/fleet/live")
def get_live_fleet():
    fleet = get_live_multimodal_fleet()
    for v in fleet:
        v["line_id"] = str(v.get("line", ""))
        v["occupancy_ratio"] = float(v.get("occupancy_rate", 0.5))
        v["passenger_count"] = int(v.get("passengers", 40))
    return {"vehicles": fleet, "timestamp": datetime.now().isoformat()}


@app.get("/api/stops/search")
def search_stops(q: str = Query(..., min_length=1), island: Optional[str] = None):
    q_clean = q.strip().lower()
    matches = []
    seen_ids = set()

    # 1. Búsqueda prioritaria en Intercambiadores y Terminales Insulares (Gran Canaria, Tenerife, Marítimo)
    for k, v in MULTIMODAL_HUBS.items():
        k_clean = k.lower()
        name_clean = v.get("name", "").lower()
        loc_clean = v.get("locality", "").lower()
        if q_clean in k_clean or q_clean in name_clean or q_clean in loc_clean:
            match_id = v.get("stop_id", k)
            if match_id not in seen_ids:
                seen_ids.add(match_id)
                matches.append({
                    "id": k,
                    "code": match_id,
                    "name": v.get("name", k),
                    "locality": v.get("locality", "Canarias"),
                    "lat": v.get("lat"),
                    "lon": v.get("lon"),
                    "is_hub": True,
                    "operators": v.get("operators", []),
                    "source": "hub",
                })

    # 2. Búsqueda en la base de datos GTFS Unificada (4.700+ paradas reales TITSA, Guaguas, etc.)
    gtfs_results = gtfs_engine.search_stops(query=q_clean, island=island, limit=12)
    for g in gtfs_results:
        gid = g["stop_id"]
        if gid not in seen_ids:
            seen_ids.add(gid)
            matches.append({
                "id": gid,
                "code": gid,
                "name": g["name"],
                "locality": g["island"],
                "lat": g["lat"],
                "lon": g["lon"],
                "agency_id": g["agency_id"],
                "is_hub": False,
                "source": "gtfs",
            })

    # 3. Búsqueda por código de poste oficial
    stop_by_code = search_stop_by_code(q_clean)
    if stop_by_code:
        code = stop_by_code.get("stop_code", "")
        if code not in seen_ids:
            seen_ids.add(code)
            item = dict(stop_by_code)
            item["code"] = code
            item["locality"] = stop_by_code.get("zone", "Gran Canaria")
            item["id"] = code
            item["source"] = "official"
            matches.append(item)

    return {"results": matches[:20]}


@app.get("/api/stops/{stop_id}/departures")
def get_departures(
    stop_id: str,
    incident_gc1: bool = False,
    is_peak: bool = False,
    rain_medianias: bool = False,
):
    now = datetime.now()

    # Si es parada de la base GTFS unificada, consultar salidas reales GTFS
    gtfs_deps = gtfs_engine.get_live_departures(stop_id=stop_id, limit=8)
    if gtfs_deps:
        return {
            "stop_id": stop_id,
            "departures": gtfs_deps,
            "timestamp": now.strftime("%H:%M:%S"),
            "source": "gtfs",
        }

    # Fallback a salidas de hub intermodal / canónico
    departures = get_live_departures_for_hub(
        stop_id=stop_id,
        hour=now.hour,
        minute=now.minute,
        is_weekend=now.weekday() >= 5,
        incident_gc1=incident_gc1,
        rain_medianias=rain_medianias,
    )
    return {
        "stop_id": stop_id,
        "departures": [d.to_dict() for d in departures],
        "timestamp": now.strftime("%H:%M:%S"),
        "source": "hub",
    }


# Endpoints dedicados de GTFS Oficial de Canarias
@app.get("/api/gtfs/overview")
def get_gtfs_overview():
    return gtfs_engine.get_summary()


@app.get("/api/gtfs/search")
def search_gtfs_stops(
    q: str = Query("", min_length=0),
    island: Optional[str] = None,
    limit: int = Query(30, ge=1, le=100),
):
    results = gtfs_engine.search_stops(query=q, island=island, limit=limit)
    return {"results": results, "count": len(results)}


@app.get("/api/gtfs/routes")
def get_gtfs_routes(agency: Optional[str] = None):
    routes = gtfs_engine.get_all_routes(agency_id=agency)
    return {"routes": routes, "count": len(routes)}


@app.get("/api/gtfs/stops/{stop_id}/departures")
def get_gtfs_stop_departures(
    stop_id: str,
    agency: Optional[str] = None,
    limit: int = Query(8, ge=1, le=20),
):
    departures = gtfs_engine.get_live_departures(stop_id=stop_id, agency_id=agency, limit=limit)
    stop_info = gtfs_engine.get_stop_by_id(stop_id, agency_id=agency)
    return {
        "stop_id": stop_id,
        "stop_info": stop_info,
        "departures": departures,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }


@app.post("/api/gtfs/sync")
def sync_gtfs_feeds(force: bool = False):
    status = download_official_feeds(force=force)
    build_unified_database(force=force)
    summary = gtfs_engine.get_summary()
    return {"status": "ok", "download_status": status, "summary": summary}


@app.post("/api/routes/plan")
def plan_route(req: RoutePlanRequest):
    try:
        plan = plan_multimodal_trip(
            origin_id=req.origin_id,
            destination_id=req.destination_id,
            is_peak=req.is_peak,
            incident_gc1=req.incident_gc1,
            target_arrival_time=req.target_arrival_time,
            walk_buffer_min=req.walk_buffer_min,
        )
        
        guarantee = calculate_guaranteed_departure_time(
            target_arrival_time_str=req.target_arrival_time,
            origin_id=req.origin_id,
            destination_id=req.destination_id,
            is_peak=req.is_peak,
            incident_gc1=req.incident_gc1,
            walk_buffer_min=req.walk_buffer_min,
        )
        
        return {
            "plan": plan,
            "guarantee": guarantee,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cards/status")
def get_card_status(
    trips: int = 11,
    day: int = 18,
    card_id: str = "WJ-35001-928"
):
    progress = calculate_free_transit_progress(trips_completed=trips, current_day_of_month=day)
    qr_b64 = generate_virtual_card_qr(card_id=card_id)
    return {
        "progress": progress,
        "card": {
            "id": card_id,
            "type": "Wawa Joven Canarias",
            "holder": "Estudiante ULPGC",
            "balance_eur": 0.0,
            "valid_thru": "10/2027",
            "qr_image_base64": qr_b64,
        }
    }


@app.get("/api/alerts")
def get_alerts():
    return {"alerts": get_live_service_alerts()}


@app.post("/api/causal/simulate")
def simulate_causal_impact(req: CausalSimRequest):
    bn = get_bayesian_net()
    evidence = {
        "Incidente_GC1": "Si" if req.incident_gc1 else "No",
        "HoraPunta": "Si" if req.is_peak else "No",
        "Lluvia_Medianias": "Si" if req.rain_medianias else "No",
    }
    
    query_vars = ["Congestion_GC1", "Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto", "Retraso_L303_Tafira"]
    probs = bn.query_probability(query_vars, evidence=evidence)
    
    return {
        "evidence": evidence,
        "probabilities": probs,
        "summary": {
            "p_flight_risk": probs["Riesgo_Vuelo_Aeropuerto"].get("Alto", 0.0),
            "p_l30_delay": probs["Retraso_L30_Sur"].get("Retraso", 0.0),
            "p_gc1_congestion": probs["Congestion_GC1"].get("Severa", 0.0),
            "p_tafira_delay": probs["Retraso_L303_Tafira"].get("Retraso", 0.0),
        }
    }


@app.get("/api/analytics/gauss-markov")
def get_gauss_markov_diagnostics():
    bundle = get_ols_bundle()
    if not bundle:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
        
    return {
        "r_squared": bundle.r_squared,
        "adj_r_squared": bundle.adj_r_squared,
        "f_statistic": bundle.f_statistic,
        "f_pvalue": bundle.f_pvalue,
        "coefficients": bundle.coefficients,
        "gauss_markov": bundle.gauss_markov_diagnostics,
    }


@app.post("/api/optimization/run")
def run_optimization(req: OptimizationRequest):
    if req.problem == "milp":
        res = solve_fleet_dispatch_milp(
            bus_budget=req.bus_budget,
            driver_hours_budget=req.driver_hours,
        )
        return {
            "problem": "MILP Despacho de Flota",
            "success": res.success,
            "total_buses": res.total_buses_dispatched,
            "total_cost_eur": res.total_cost_eur,
            "coverage_ratio": res.coverage_ratio,
            "corridor_dispatches": res.corridor_dispatches,
            "passengers_served": res.passengers_served,
            "passengers_unmet": res.passengers_unmet,
            "shadow_prices": res.shadow_prices,
            "solver": res.solver_method,
        }
        
    elif req.problem == "newton":
        gd_res = optimize_bpr_gradient_descent(learning_rate=0.0005, max_iter=80)
        newton_res = optimize_bpr_newton(max_iter=15)
        return {
            "problem": "Calibración BPR No Lineal (Tema 2)",
            "gradient_descent": {
                "iterations": gd_res.iterations,
                "final_loss": gd_res.final_loss,
                "params": [round(float(p), 4) for p in gd_res.optimal_params],
                "convergence": gd_res.convergence_rate,
            },
            "newton_method": {
                "iterations": newton_res.iterations,
                "final_loss": newton_res.final_loss,
                "params": [round(float(p), 4) for p in newton_res.optimal_params],
                "convergence": newton_res.convergence_rate,
            },
            "speedup_factor": round(gd_res.iterations / max(1, newton_res.iterations), 1),
        }
        
    elif req.problem == "lagrange":
        res = solve_lagrangian_frequency_allocation(fuel_budget=350.0)
        return {
            "problem": "Multiplicadores de Lagrange (Tema 3.2)",
            "shadow_price_lambda": res["shadow_price_lambda"],
            "optimal_frequencies": res["optimal_frequencies"],
            "fuel_consumed": res["total_fuel_consumed"],
            "budget": res["budget_limit"],
        }
        
    elif req.problem in ["tsp_sa", "tsp_ga"]:
        sa_res = solve_tsp_simulated_annealing(initial_temp=100.0, alpha=0.995, max_iter=2500)
        ga_res = solve_tsp_genetic_algorithm(population_size=60, generations=80)
        return {
            "problem": "TSP Circular Insular 10 Hubs (Tema 4)",
            "simulated_annealing": {
                "best_distance_km": round(sa_res.best_distance_km, 2),
                "iterations": sa_res.iterations_completed,
                "route": sa_res.best_route,
            },
            "genetic_algorithm": {
                "best_distance_km": round(ga_res.best_distance_km, 2),
                "generations": ga_res.generations_completed,
                "route": ga_res.best_route,
            }
        }
        
    raise HTTPException(status_code=400, detail=f"Problema desconocido: {req.problem}")


# Montar la aplicación React compilada (SPA) si existe en frontend/dist
from fastapi.staticfiles import StaticFiles

frontend_dist = ROOT_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
