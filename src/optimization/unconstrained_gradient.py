"""Módulo de Métodos de Optimización Sin Restricciones.

Tema 2 del temario de Optimización ULPGC:
- 2.3 Métodos de descenso por gradiente
- 2.4 Método de Newton (Hessiano exacto)
- 2.5 Métodos cuasi-Newton (BFGS)

Aplica descenso por gradiente y método de Newton con matriz Hessiana analítica
para calibrar la función no lineal de coste de viaje y congestión BPR (Bureau of Public Roads)
en la red de carreteras de Gran Canaria.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize


@dataclass
class OptimizationTrajectory:
    method: str
    iterations: int
    optimal_params: np.ndarray
    final_loss: float
    loss_history: List[float]
    grad_norm_history: List[float]
    param_history: List[List[float]]
    converged: bool
    convergence_rate: str


def generate_bpr_synthetic_data(num_samples: int = 500, random_seed: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Genera datos empíricos de distancias (d), saturación de tráfico (v/c) y tiempos reales (y)."""
    np.random.seed(random_seed)
    distances = np.random.uniform(5.0, 45.0, num_samples)  # km
    saturation = np.random.uniform(0.2, 1.3, num_samples)  # ratio v/c
    t0 = 5.0  # tiempo base en paradas (min)
    # Parámetros verdaderos: theta_1 = 1.15 (min/km), theta_2 = 14.5 (penalización congestión)
    noise = np.random.normal(0, 1.5, num_samples)
    y = t0 + 1.15 * distances + 14.5 * (saturation ** 4) + noise
    return distances, saturation, y


def bpr_loss_function(theta: np.ndarray, distances: np.ndarray, saturation: np.ndarray, y: np.ndarray, t0: float = 5.0) -> float:
    """Función de pérdida cuadrática media MSE: f(theta)."""
    y_pred = t0 + theta[0] * distances + theta[1] * (saturation ** 4)
    residuals = y - y_pred
    return float(np.mean(residuals ** 2))


def bpr_gradient(theta: np.ndarray, distances: np.ndarray, saturation: np.ndarray, y: np.ndarray, t0: float = 5.0) -> np.ndarray:
    """Gradiente analítico nabla f(theta) in R^2."""
    sat4 = saturation ** 4
    y_pred = t0 + theta[0] * distances + theta[1] * sat4
    residuals = y - y_pred
    N = len(y)
    grad_0 = - (2.0 / N) * np.sum(residuals * distances)
    grad_1 = - (2.0 / N) * np.sum(residuals * sat4)
    return np.array([grad_0, grad_1])


def bpr_hessian(theta: np.ndarray, distances: np.ndarray, saturation: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Matriz Hessiana analítica H in R^(2x2).
    
    Notar que para pérdida MSE en un modelo lineal en theta, la Hessiana es constante y semidefinida positiva.
    """
    sat4 = saturation ** 4
    N = len(y)
    H00 = (2.0 / N) * np.sum(distances ** 2)
    H01 = (2.0 / N) * np.sum(distances * sat4)
    H10 = H01
    H11 = (2.0 / N) * np.sum(sat4 ** 2)
    return np.array([[H00, H01], [H10, H11]])


def optimize_bpr_gradient_descent(
    init_theta: Optional[np.ndarray] = None,
    learning_rate: float = 0.0005,
    max_iters: int = 150,
    tol: float = 1e-4,
) -> OptimizationTrajectory:
    """Método de Descenso por Gradiente con tamaño de paso y registro de convergencia."""
    distances, saturation, y = generate_bpr_synthetic_data()
    theta = np.array([0.2, 2.0]) if init_theta is None else np.array(init_theta, dtype=float)

    loss_history = []
    grad_norm_history = []
    param_history = []

    converged = False
    for it in range(max_iters):
        loss = bpr_loss_function(theta, distances, saturation, y)
        grad = bpr_gradient(theta, distances, saturation, y)
        grad_norm = float(np.linalg.norm(grad))

        loss_history.append(loss)
        grad_norm_history.append(grad_norm)
        param_history.append(theta.tolist())

        if grad_norm < tol:
            converged = True
            break

        # Actualización por descenso por gradiente: theta^(k+1) = theta^k - eta * grad
        theta = theta - learning_rate * grad

    return OptimizationTrajectory(
        method="Descenso por Gradiente (Tema 2.3)",
        iterations=len(loss_history),
        optimal_params=theta,
        final_loss=loss_history[-1],
        loss_history=loss_history,
        grad_norm_history=grad_norm_history,
        param_history=param_history,
        converged=converged,
        convergence_rate="Lineal (O(k))",
    )


def optimize_bpr_newton(
    init_theta: Optional[np.ndarray] = None,
    max_iters: int = 20,
    tol: float = 1e-5,
) -> OptimizationTrajectory:
    """Método de Newton de segundo orden con inversión de la matriz Hessiana: theta^(k+1) = theta^k - H^(-1) grad."""
    distances, saturation, y = generate_bpr_synthetic_data()
    theta = np.array([0.2, 2.0]) if init_theta is None else np.array(init_theta, dtype=float)

    loss_history = []
    grad_norm_history = []
    param_history = []

    converged = False
    for it in range(max_iters):
        loss = bpr_loss_function(theta, distances, saturation, y)
        grad = bpr_gradient(theta, distances, saturation, y)
        H = bpr_hessian(theta, distances, saturation, y)
        grad_norm = float(np.linalg.norm(grad))

        loss_history.append(loss)
        grad_norm_history.append(grad_norm)
        param_history.append(theta.tolist())

        if grad_norm < tol:
            converged = True
            break

        # Paso de Newton
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(H) @ grad

        theta = theta - step

    return OptimizationTrajectory(
        method="Método de Newton 2º Orden (Tema 2.4)",
        iterations=len(loss_history),
        optimal_params=theta,
        final_loss=loss_history[-1],
        loss_history=loss_history,
        grad_norm_history=grad_norm_history,
        param_history=param_history,
        converged=converged,
        convergence_rate="Cuadrática (O(k²))",
    )
