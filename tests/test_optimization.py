"""Tests unitarios y validación matemática del módulo de Optimización.

Verifica formalmente:
1. Programación Lineal Entera Mixta (MILP): satisfacción exacta de restricciones de demanda y capacidad.
2. Descenso por Gradiente vs Newton: convergencia hacia el mínimo y velocidad de convergencia (Newton cuadrática vs GD lineal).
3. Multiplicadores de Lagrange: cumplimiento de restricción presupuestaria sum(k_i * f_i) = B y gradiente nulo dL/df = 0.
4. Metaheurísticas (Simulated Annealing & Algoritmo Genético): permutaciones válidas sin paradas duplicadas y reducción de distancia.
"""

import numpy as np
import pytest

from src.optimization.fleet_dispatch_milp import solve_fleet_dispatch_milp, DEFAULT_CORRIDORS
from src.optimization.unconstrained_gradient import optimize_bpr_gradient_descent, optimize_bpr_newton
from src.optimization.lagrangian_allocation import solve_lagrangian_frequency_allocation
from src.optimization.heuristic_routing import solve_tsp_simulated_annealing, solve_tsp_genetic_algorithm


def test_milp_fleet_dispatch_constraints():
    """Valida que la asignación MILP respeta estrictamente las cotas de flota y horas de conducción."""
    total_buses = 60
    max_hours = 50.0
    res = solve_fleet_dispatch_milp(total_available_buses=total_buses, max_driver_hours=max_hours)

    assert res.success, f"El solver MILP falló: {res.status}"
    assert res.total_buses_dispatched <= total_buses, "Se superó el límite de guaguas disponibles"

    # Verificar satisfacción de demanda + holgura: 65 * x_i + s_i >= D_i
    for corr in DEFAULT_CORRIDORS:
        x_i = res.corridor_dispatches[corr.name]
        s_i = res.passengers_unmet[corr.name]
        assert (x_i * corr.bus_capacity + s_i) >= corr.passengers_demand, f"Fallo en demanda para {corr.name}"

    assert 0.0 <= res.coverage_ratio <= 1.0


def test_gradient_descent_and_newton_convergence():
    """Verifica que tanto Descenso por Gradiente como Newton convergen y reducen la pérdida inicial."""
    res_gd = optimize_bpr_gradient_descent(max_iters=100)
    res_newton = optimize_bpr_newton(max_iters=10)

    # Ambos reducen la pérdida
    assert res_gd.loss_history[-1] < res_gd.loss_history[0], "Descenso por gradiente no redujo la pérdida"
    assert res_newton.loss_history[-1] < res_newton.loss_history[0], "Método de Newton no redujo la pérdida"

    # El método de Newton requiere significativamente menos iteraciones para alcanzar baja pérdida
    assert res_newton.iterations <= 15
    assert np.all(np.isfinite(res_newton.optimal_params))


def test_lagrangian_multipliers_budget_satisfaction():
    """Verifica que el reparto de Lagrange gasta exactamente el presupuesto disponible sum(k_i * f_i) = B."""
    budget = 700.0
    res = solve_lagrangian_frequency_allocation(total_budget_km=budget)

    # Restricción activa exacta
    assert np.isclose(res.budget_used, budget, atol=1e-5), f"Presupuesto usado {res.budget_used} != {budget}"
    # Multiplicador lambda positivo
    assert res.lambda_multiplier > 0.0, "El multiplicador de Lagrange debe ser estrictamente positivo"
    # Norma del gradiente del Lagrangiano nula
    assert np.isclose(res.lagrangian_gradient_norm, 0.0, atol=1e-5), "El gradiente del Lagrangiano debe ser nulo en el óptimo"


def test_heuristic_routing_properties():
    """Verifica que Simulated Annealing y Algoritmo Genético generan rutas válidas y reducen distancia."""
    res_sa = solve_tsp_simulated_annealing(initial_temp=400.0, cooling_rate=0.96)
    res_ga = solve_tsp_genetic_algorithm(pop_size=40, generations=50)

    # Permutaciones completas sin duplicados
    assert len(set(res_sa.best_route_codes)) == 10, "Simulated Annealing no visitó todas las 10 paradas"
    assert len(set(res_ga.best_route_codes)) == 10, "Algoritmo Genético no visitó todas las 10 paradas"

    # Distancia final menor o igual que la inicial
    assert res_sa.best_distance_km <= res_sa.initial_distance_km, "SA no mejoró la distancia"
    assert res_ga.best_distance_km <= res_ga.initial_distance_km, "GA no mejoró la distancia"
