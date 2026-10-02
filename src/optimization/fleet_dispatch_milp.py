"""Módulo de Programación Lineal y Entera Mixta (MILP / Método Simplex).

Temas 1 y 3 del temario de Optimización ULPGC:
- 1.3 Programación lineal
- 1.5 Programación entera
- 3.3 Programación lineal
- 3.4 Método Simplex
- 3.5 Programación entera

Aplica MILP para resolver la asignación óptima de expediciones de guaguas y conductores
en los principales corredores de Gran Canaria durante horas punta insulares.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
from scipy.optimize import LinearConstraint, milp, linprog


@dataclass
class CorridorDemand:
    id: str
    name: str
    passengers_demand: int
    trip_cost_eur: float
    trip_duration_hours: float
    penalty_unmet_pax: float
    bus_capacity: int = 65


@dataclass
class DispatchResult:
    status: str
    success: bool
    total_cost_eur: float
    total_buses_dispatched: int
    corridor_dispatches: Dict[str, int]
    passengers_served: Dict[str, int]
    passengers_unmet: Dict[str, int]
    coverage_ratio: float
    shadow_prices: Dict[str, float]
    solver_method: str


DEFAULT_CORRIDORS: List[CorridorDemand] = [
    CorridorDemand(
        id="GC1_SUR",
        name="Corredor Sur (GC-1: San Telmo ➔ Maspalomas)",
        passengers_demand=1850,
        trip_cost_eur=48.0,
        trip_duration_hours=0.85,
        penalty_unmet_pax=12.0,
        bus_capacity=65,
    ),
    CorridorDemand(
        id="GC110_TAFIRA",
        name="Corredor Universitario (GC-110: San Telmo ➔ Campus Tafira)",
        passengers_demand=1420,
        trip_cost_eur=32.0,
        trip_duration_hours=0.55,
        penalty_unmet_pax=15.0,  # Alta penalización por exámenes ULPGC
        bus_capacity=65,
    ),
    CorridorDemand(
        id="GC2_NORTE",
        name="Corredor Norte (GC-2: San Telmo ➔ Gáldar / Agaete)",
        passengers_demand=980,
        trip_cost_eur=42.0,
        trip_duration_hours=0.75,
        penalty_unmet_pax=10.0,
        bus_capacity=65,
    ),
    CorridorDemand(
        id="AEROPUERTO",
        name="Corredor Exprés Aeropuerto (LPA Gando)",
        passengers_demand=750,
        trip_cost_eur=36.0,
        trip_duration_hours=0.45,
        penalty_unmet_pax=20.0,  # Máxima penalización por riesgo de vuelos
        bus_capacity=65,
    ),
    CorridorDemand(
        id="MEDIANIAS",
        name="Corredor Medianías (GC-15: Santa Brígida ➔ San Mateo)",
        passengers_demand=460,
        trip_cost_eur=38.0,
        trip_duration_hours=0.65,
        penalty_unmet_pax=8.0,
        bus_capacity=65,
    ),
]


def solve_fleet_dispatch_milp(
    corridors: Optional[List[CorridorDemand]] = None,
    total_available_buses: int = 75,
    max_driver_hours: float = 60.0,
) -> DispatchResult:
    """Resuelve el problema de asignación de flota de Global mediante MILP.
    
    Variables de decisión:
      x_i: número entero de viajes de guagua asignados al corredor i (x_i in Z_>=0)
      s_i: número continuo de pasajeros desatendidos en el corredor i (s_i >= 0)
      
    Función objetivo:
      min sum_i (c_i * x_i + p_i * s_i)
      
    Restricciones:
      1. Cobertura de demanda: 65 * x_i + s_i >= D_i (para cada corredor)
      2. Límite de flota: sum_i x_i <= total_available_buses
      3. Límite de horas de conductor: sum_i (tau_i * x_i) <= max_driver_hours
    """
    corr_list = corridors or DEFAULT_CORRIDORS
    m = len(corr_list)

    # Vector de variables: [x_0, ..., x_{m-1}, s_0, ..., s_{m-1}]
    # Longitud: 2 * m
    c = np.zeros(2 * m)
    for i, corr in enumerate(corr_list):
        c[i] = corr.trip_cost_eur  # Coste viaje x_i
        c[m + i] = corr.penalty_unmet_pax  # Penalización s_i

    # Integridad: 1 para entero (x_i), 0 para continuo (s_i)
    integrality = np.zeros(2 * m)
    integrality[:m] = 1

    # Límites de variables: x_i >= 0, s_i >= 0
    lb = np.zeros(2 * m)
    ub = np.full(2 * m, np.inf)

    # Restricciones lineales:
    # 1. Demanda: 65 * x_i + s_i >= D_i (m restricciones)
    # 2. Flota: sum x_i <= B_fleet (1 restricción)
    # 3. Horas: sum tau_i * x_i <= H_max (1 restricción)
    num_constraints = m + 2
    A = np.zeros((num_constraints, 2 * m))
    lhs = np.zeros(num_constraints)
    rhs = np.zeros(num_constraints)

    # 1. Demanda
    for i, corr in enumerate(corr_list):
        A[i, i] = corr.bus_capacity
        A[i, m + i] = 1.0
        lhs[i] = corr.passengers_demand
        rhs[i] = np.inf

    # 2. Límite de flota
    A[m, :m] = 1.0
    lhs[m] = -np.inf
    rhs[m] = float(total_available_buses)

    # 3. Límite de horas de conductor
    for i, corr in enumerate(corr_list):
        A[m + 1, i] = corr.trip_duration_hours
    lhs[m + 1] = -np.inf
    rhs[m + 1] = float(max_driver_hours)

    constraints = LinearConstraint(A, lhs, rhs)

    # Resolver con scipy.optimize.milp (Solver HiGHS)
    res_milp = milp(c=c, integrality=integrality, constraints=constraints)

    # Relajación lineal continua (Método Simplex / HiGHS-LP) para precios sombra duales
    # A_eq_ub: reescribir para linprog
    # lhs <= A x <= rhs
    A_lp = []
    b_lp = []
    # Demanda: -65 * x_i - s_i <= -D_i
    for i, corr in enumerate(corr_list):
        row = np.zeros(2 * m)
        row[i] = -corr.bus_capacity
        row[m + i] = -1.0
        A_lp.append(row)
        b_lp.append(-corr.passengers_demand)
    # Flota: sum x_i <= total_buses
    row_f = np.zeros(2 * m)
    row_f[:m] = 1.0
    A_lp.append(row_f)
    b_lp.append(float(total_available_buses))
    # Horas: sum tau_i * x_i <= max_hours
    row_h = np.zeros(2 * m)
    for i, corr in enumerate(corr_list):
        row_h[i] = corr.trip_duration_hours
    A_lp.append(row_h)
    b_lp.append(float(max_driver_hours))

    bounds_lp = [(0, None) for _ in range(2 * m)]
    res_lp = linprog(c, A_ub=np.array(A_lp), b_ub=np.array(b_lp), bounds=bounds_lp, method="highs-ds")

    shadow_prices = {}
    if res_lp.success and hasattr(res_lp, "ineqlin"):
        marginals = res_lp.ineqlin.marginals
        shadow_prices["Precio_Sombra_Flota_EUR_Guagua"] = float(abs(marginals[m])) if len(marginals) > m else 0.0
        shadow_prices["Precio_Sombra_Horas_EUR_Hora"] = float(abs(marginals[m + 1])) if len(marginals) > m + 1 else 0.0

    if not res_milp.success:
        return DispatchResult(
            status="Infeasible",
            success=False,
            total_cost_eur=0.0,
            total_buses_dispatched=0,
            corridor_dispatches={},
            passengers_served={},
            passengers_unmet={},
            coverage_ratio=0.0,
            shadow_prices=shadow_prices,
            solver_method="scipy.optimize.milp (HiGHS)",
        )

    sol = res_milp.x
    x_opt = np.round(sol[:m]).astype(int)
    s_opt = np.maximum(0, np.round(sol[m : 2 * m])).astype(int)

    dispatches = {}
    served = {}
    unmet = {}
    total_demand = 0
    total_served = 0

    for i, corr in enumerate(corr_list):
        dispatches[corr.name] = int(x_opt[i])
        unmet[corr.name] = int(s_opt[i])
        actual_served = min(corr.passengers_demand, int(x_opt[i] * corr.bus_capacity))
        served[corr.name] = actual_served
        total_demand += corr.passengers_demand
        total_served += actual_served

    coverage = total_served / max(1, total_demand)

    return DispatchResult(
        status="Optimal",
        success=True,
        total_cost_eur=float(res_milp.fun),
        total_buses_dispatched=int(np.sum(x_opt)),
        corridor_dispatches=dispatches,
        passengers_served=served,
        passengers_unmet=unmet,
        coverage_ratio=float(coverage),
        shadow_prices=shadow_prices,
        solver_method="scipy.optimize.milp (HiGHS / Método Simplex Dual)",
    )
