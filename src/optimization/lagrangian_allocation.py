"""Módulo de Optimización con Restricciones: Multiplicadores de Lagrange.

Tema 3 del temario de Optimización ULPGC:
- 3.2 Multiplicadores de Lagrange
- Interpretación económica del multiplicador lambda (coste sombra / utilidad marginal)

Aplica el método de Lagrange para resolver la asignación continua de frecuencias de servicio
f_i (expediciones/hora) maximizando la utilidad logarítmica de los viajeros de Gran Canaria
sujeta a una restricción de presupuesto de combustible y kilómetros:
    max sum_i w_i * ln(f_i)   s.a.   sum_i k_i * f_i = B
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import numpy as np
from scipy.optimize import minimize


@dataclass
class LineWeight:
    line_name: str
    weight_social: float  # Importancia social / afluencia de pasajeros w_i
    km_per_trip: float    # Coste en kilómetros k_i


@dataclass
class LagrangeResult:
    optimal_frequencies: Dict[str, float]
    optimal_utility: float
    lambda_multiplier: float
    budget_used: float
    budget_total: float
    lagrangian_gradient_norm: float
    interpretation_lambda: str


DEFAULT_LINES = [
    LineWeight("Línea 30 (GC-1 Las Palmas ➔ Faro Maspalomas)", weight_social=4.5, km_per_trip=54.0),
    LineWeight("Línea 50 (GC-1 Exprés Directo Sur)", weight_social=3.8, km_per_trip=50.0),
    LineWeight("Línea 303 (GC-110 Campus Tafira ➔ San Mateo)", weight_social=4.2, km_per_trip=28.0),
    LineWeight("Línea 103 (GC-2 Norte Las Palmas ➔ Agaete)", weight_social=3.0, km_per_trip=36.0),
    LineWeight("Línea 60 (San Telmo ➔ Aeropuerto LPA)", weight_social=3.5, km_per_trip=24.0),
]


def solve_lagrangian_frequency_allocation(
    lines: Optional[List[LineWeight]] = None,
    total_budget_km: float = 650.0,
) -> LagrangeResult:
    """Calcula analítica y numéricamente la solución de Lagrange para el reparto de frecuencias."""
    line_list = lines or DEFAULT_LINES
    w = np.array([l.weight_social for l in line_list])
    k = np.array([l.km_per_trip for l in line_list])
    B = float(total_budget_km)

    # 1. Solución analítica con Multiplicadores de Lagrange
    # grad L = 0 => w_i / f_i - lambda * k_i = 0 => f_i = w_i / (lambda * k_i)
    # sum k_i * f_i = sum (w_i / lambda) = (sum w_i) / lambda = B
    # => lambda* = (sum w_i) / B
    lambda_star = float(np.sum(w) / B)
    f_star = w / (lambda_star * k)

    # Comprobación de restricción: sum k_i * f_i
    budget_used = float(np.sum(k * f_star))

    # Utilidad óptima
    optimal_utility = float(np.sum(w * np.log(f_star)))

    # Norma del gradiente del Lagrangiano
    # dL/df_i = w_i / f_i - lambda * k_i
    grad_L = (w / f_star) - lambda_star * k
    grad_norm = float(np.linalg.norm(grad_L))

    freq_dict = {line_list[i].line_name: float(np.round(f_star[i], 2)) for i in range(len(line_list))}

    interpretation = (
        f"λ* = {lambda_star:.4f}. Representa la utilidad marginal que ganaría la red de Global "
        f"por cada kilómetro adicional asignado al presupuesto de combustible (∂U*/∂B = λ*)."
    )

    return LagrangeResult(
        optimal_frequencies=freq_dict,
        optimal_utility=optimal_utility,
        lambda_multiplier=lambda_star,
        budget_used=budget_used,
        budget_total=B,
        lagrangian_gradient_norm=grad_norm,
        interpretation_lambda=interpretation,
    )
