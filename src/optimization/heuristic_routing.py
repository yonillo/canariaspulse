"""Módulo de Métodos Heurísticos y Metaheurísticas.

Tema 4 del temario de Optimización ULPGC:
- 4.2 Algoritmos evolutivos
- 4.3 Algoritmos genéticos
- 4.6 Simulated annealing (Recocido simulado)

Aplica metaheurísticas para resolver el Problema del Viajante de Comercio (TSP)
y enrutamiento de expediciones de refuerzo escolar e inspección entre los nodos
intermodales clave de Gran Canaria.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import numpy as np


@dataclass
class HeuristicResult:
    method: str
    best_route_names: List[str]
    best_route_codes: List[str]
    initial_distance_km: float
    best_distance_km: float
    improvement_pct: float
    cost_history: List[float]
    iterations_run: int


KEY_HUBS_COORDS = [
    {"code": "1001", "name": "San Telmo", "lat": 28.1068, "lon": -15.4172},
    {"code": "1002", "name": "Santa Catalina", "lat": 28.1408, "lon": -15.4298},
    {"code": "2015", "name": "Campus Tafira", "lat": 28.0722, "lon": -15.4542},
    {"code": "2104", "name": "Santa Brígida", "lat": 28.0336, "lon": -15.5005},
    {"code": "2201", "name": "San Mateo", "lat": 28.0094, "lon": -15.5322},
    {"code": "3001", "name": "Telde", "lat": 27.9995, "lon": -15.4190},
    {"code": "4001", "name": "Aeropuerto LPA", "lat": 27.9348, "lon": -15.3882},
    {"code": "4205", "name": "Vecindario", "lat": 27.8465, "lon": -15.4411},
    {"code": "5020", "name": "Faro Maspalomas", "lat": 27.7356, "lon": -15.5997},
    {"code": "7001", "name": "Arucas", "lat": 28.1189, "lon": -15.5236},
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia ortodrómica en kilómetros."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    return float(2.0 * R * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0))))


def compute_distance_matrix(hubs: List[Dict[str, Any]]) -> np.ndarray:
    n = len(hubs)
    dist_mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_mat[i, j] = haversine_km(hubs[i]["lat"], hubs[i]["lon"], hubs[j]["lat"], hubs[j]["lon"])
    return dist_mat


def route_distance(route: List[int], dist_matrix: np.ndarray) -> float:
    """Calcula la distancia total del circuito cerrado (regreso al origen)."""
    d = 0.0
    n = len(route)
    for i in range(n):
        d += dist_matrix[route[i], route[(i + 1) % n]]
    return float(d)


def solve_tsp_simulated_annealing(
    hubs: Optional[List[Dict[str, Any]]] = None,
    initial_temp: float = 500.0,
    cooling_rate: float = 0.97,
    min_temp: float = 0.5,
    random_seed: int = 42,
) -> HeuristicResult:
    """Resuelve el TSP de la red de Global mediante Recocido Simulado (Simulated Annealing)."""
    np.random.seed(random_seed)
    h_list = hubs or KEY_HUBS_COORDS
    n = len(h_list)
    dist_matrix = compute_distance_matrix(h_list)

    # Ruta inicial fija o aleatoria
    current_route = list(range(n))
    current_dist = route_distance(current_route, dist_matrix)
    initial_dist = current_dist

    best_route = list(current_route)
    best_dist = current_dist

    temp = initial_temp
    cost_history = [current_dist]
    iters = 0

    while temp > min_temp:
        # Movimiento de vecindad 2-opt: invertir subsecuencia
        i, j = sorted(np.random.choice(n, size=2, replace=False))
        neighbor = list(current_route)
        neighbor[i : j + 1] = reversed(neighbor[i : j + 1])
        neighbor_dist = route_distance(neighbor, dist_matrix)

        delta_e = neighbor_dist - current_dist

        # Criterio de Metropolis
        if delta_e < 0 or np.random.rand() < np.exp(-delta_e / temp):
            current_route = neighbor
            current_dist = neighbor_dist
            if current_dist < best_dist:
                best_dist = current_dist
                best_route = list(current_route)

        cost_history.append(current_dist)
        temp *= cooling_rate
        iters += 1

    improvement = ((initial_dist - best_dist) / initial_dist) * 100.0

    return HeuristicResult(
        method="Simulated Annealing (Recocido Simulado - Tema 4.6)",
        best_route_names=[h_list[i]["name"] for i in best_route],
        best_route_codes=[h_list[i]["code"] for i in best_route],
        initial_distance_km=float(np.round(initial_dist, 2)),
        best_distance_km=float(np.round(best_dist, 2)),
        improvement_pct=float(np.round(improvement, 2)),
        cost_history=cost_history,
        iterations_run=iters,
    )


def solve_tsp_genetic_algorithm(
    hubs: Optional[List[Dict[str, Any]]] = None,
    pop_size: int = 50,
    generations: int = 70,
    mutation_rate: float = 0.20,
    random_seed: int = 42,
) -> HeuristicResult:
    """Resuelve el TSP de la red de Global mediante Algoritmo Genético con cruce OX y mutación Swap."""
    np.random.seed(random_seed)
    h_list = hubs or KEY_HUBS_COORDS
    n = len(h_list)
    dist_matrix = compute_distance_matrix(h_list)

    # 1. Inicialización de población
    population = [np.random.permutation(n).tolist() for _ in range(pop_size)]
    fitness = [route_distance(ind, dist_matrix) for ind in population]

    best_idx = int(np.argmin(fitness))
    best_route = list(population[best_idx])
    best_dist = float(fitness[best_idx])
    initial_dist = best_dist

    cost_history = [best_dist]

    for gen in range(generations):
        new_population = [best_route]  # Elitismo: conservar el mejor

        while len(new_population) < pop_size:
            # Selección por torneo
            t_size = 3
            t_candidates_1 = np.random.choice(pop_size, size=t_size, replace=False)
            parent_1 = population[min(t_candidates_1, key=lambda idx: fitness[idx])]

            t_candidates_2 = np.random.choice(pop_size, size=t_size, replace=False)
            parent_2 = population[min(t_candidates_2, key=lambda idx: fitness[idx])]

            # Cruce Order Crossover (OX)
            i, j = sorted(np.random.choice(n, size=2, replace=False))
            child = [-1] * n
            child[i : j + 1] = parent_1[i : j + 1]
            remaining = [gene for gene in parent_2 if gene not in child]
            fill_idx = 0
            for pos in range(n):
                if child[pos] == -1:
                    child[pos] = remaining[fill_idx]
                    fill_idx += 1

            # Mutación por intercambio (Swap)
            if np.random.rand() < mutation_rate:
                m1, m2 = np.random.choice(n, size=2, replace=False)
                child[m1], child[m2] = child[m2], child[m1]

            new_population.append(child)

        population = new_population
        fitness = [route_distance(ind, dist_matrix) for ind in population]
        curr_best_idx = int(np.argmin(fitness))

        if fitness[curr_best_idx] < best_dist:
            best_dist = float(fitness[curr_best_idx])
            best_route = list(population[curr_best_idx])

        cost_history.append(best_dist)

    improvement = ((initial_dist - best_dist) / initial_dist) * 100.0

    return HeuristicResult(
        method="Algoritmo Genético (Tema 4.3)",
        best_route_names=[h_list[i]["name"] for i in best_route],
        best_route_codes=[h_list[i]["code"] for i in best_route],
        initial_distance_km=float(np.round(initial_dist, 2)),
        best_distance_km=float(np.round(best_dist, 2)),
        improvement_pct=float(np.round(improvement, 2)),
        cost_history=cost_history,
        iterations_run=generations,
    )
