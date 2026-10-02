"""Módulo de Métodos de Optimización Matemática para la Red de Transporte de Gran Canaria.

Alineado con el temario académico de Optimización (3º Grado en Ciencia e Ingeniería de Datos, ULPGC):
- Tema 1 & 3: Programación Lineal y Entera Mixta (MILP / Método Simplex / HiGHS).
- Tema 2: Métodos sin restricciones (Descenso por Gradiente y Método de Newton con matriz Hessiana).
- Tema 3: Métodos con restricciones (Multiplicadores de Lagrange y coste sombra).
- Tema 4: Métodos Heurísticos y Metaheurísticas (Simulated Annealing y Algoritmos Genéticos para rutas).
"""

from __future__ import annotations

from src.optimization.fleet_dispatch_milp import solve_fleet_dispatch_milp, DispatchResult
from src.optimization.unconstrained_gradient import (
    optimize_bpr_gradient_descent,
    optimize_bpr_newton,
    OptimizationTrajectory,
)
from src.optimization.lagrangian_allocation import solve_lagrangian_frequency_allocation
from src.optimization.heuristic_routing import (
    solve_tsp_simulated_annealing,
    solve_tsp_genetic_algorithm,
    HeuristicResult,
)

__all__ = [
    "solve_fleet_dispatch_milp",
    "DispatchResult",
    "optimize_bpr_gradient_descent",
    "optimize_bpr_newton",
    "OptimizationTrajectory",
    "solve_lagrangian_frequency_allocation",
    "solve_tsp_simulated_annealing",
    "solve_tsp_genetic_algorithm",
    "HeuristicResult",
]
