"""Módulo de Regresión Lineal Bayesiana y Distribución Predictiva a Posteriori (Bloque 2 Temas 3 y 4).

Implementa:
- Modelo lineal probabilístico con distribución a priori Gaussiana en los pesos:
  beta ~ N(mu_0, Sigma_0)
- Cálculo exacto de los parámetros a posteriori (media mu_N y covarianza Sigma_N).
- Distribución predictiva a posteriori para nuevos trayectos:
  p(y_* | x_*, D) ~ N(mu_pred, sigma_pred^2)
  donde sigma_pred^2 = sigma_ruido^2 + x_*^T Sigma_N x_* (combina varianza epistémica y aleatoria).
- Muestreo de Monte Carlo para obtener intervalos de credibilidad HDI (Highest Density Interval) del 95%.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class BayesianPrediction:
    mean_travel_time: float
    epistemic_uncertainty: float
    aleatoric_uncertainty: float
    total_std: float
    credible_interval_95: Tuple[float, float]
    reliability_level: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_travel_time_min": round(self.mean_travel_time, 2),
            "epistemic_std": round(self.epistemic_uncertainty, 2),
            "aleatoric_std": round(self.aleatoric_uncertainty, 2),
            "total_std": round(self.total_std, 2),
            "credible_interval_95": (round(self.credible_interval_95[0], 2), round(self.credible_interval_95[1], 2)),
            "reliability_level": self.reliability_level,
        }


class BayesianLinearRegressor:
    """Regresor lineal bayesiano analítico con priors normales en los coeficientes."""

    def __init__(self, alpha_prior: float = 1.0, beta_noise: float = 0.5):
        """alpha_prior: Precisión a priori de los pesos (Sigma_0 = (1/alpha_prior) * I).

        beta_noise: Precisión del ruido de las observaciones (1 / sigma^2).
        """
        self.alpha_prior = alpha_prior
        self.beta_noise = beta_noise
        self.mu_N: Optional[np.ndarray] = None
        self.Sigma_N: Optional[np.ndarray] = None
        self.feature_names: List[str] = []

    def fit(self, X: np.ndarray | pd.DataFrame, y: np.ndarray | pd.Series) -> BayesianLinearRegressor:
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
            X_mat = X.values
        else:
            X_mat = np.asarray(X)
            self.feature_names = [f"x{i}" for i in range(X_mat.shape[1])]

        y_vec = np.asarray(y).ravel()
        n_features = X_mat.shape[1]

        # Prior: mu_0 = 0, Sigma_0_inv = alpha_prior * I
        Sigma_0_inv = self.alpha_prior * np.eye(n_features)

        # Posterior: Sigma_N_inv = Sigma_0_inv + beta * X^T * X
        XTX = X_mat.T @ X_mat
        Sigma_N_inv = Sigma_0_inv + self.beta_noise * XTX
        self.Sigma_N = np.linalg.inv(Sigma_N_inv)

        # mu_N = beta * Sigma_N * X^T * y
        self.mu_N = self.beta_noise * (self.Sigma_N @ (X_mat.T @ y_vec))
        return self

    def predict_with_uncertainty(self, x_new: np.ndarray | List[float], n_mc_samples: int = 1500) -> BayesianPrediction:
        """Calcula la media predictiva y el intervalo de credibilidad al 95% para un nuevo trayecto."""
        if self.mu_N is None or self.Sigma_N is None:
            raise ValueError("El modelo bayesiano debe ser entrenado primero.")

        x = np.asarray(x_new, dtype=float).reshape(1, -1)

        # Media predictiva
        y_mean = float((x @ self.mu_N).item())

        # Varianza epistémica (incertidumbre sobre los parámetros beta)
        var_epistemic = float((x @ self.Sigma_N @ x.T).item())

        # Varianza aleatoria (ruido inherente al tráfico en carretera)
        var_aleatoric = 1.0 / self.beta_noise

        total_var = var_epistemic + var_aleatoric
        total_std = np.sqrt(total_var)

        # Muestreo Monte Carlo de la distribución predictiva a posteriori
        samples = np.random.normal(loc=y_mean, scale=total_std, size=n_mc_samples)
        ci_lower = float(np.percentile(samples, 2.5))
        ci_upper = float(np.percentile(samples, 97.5))

        # Indicador para usuario final ("Fiabilidad Alta", "Media", "Baja")
        interval_width = ci_upper - ci_lower
        if interval_width < 12.0:
            reliability = "Alta (Alta Certidumbre)"
        elif interval_width < 22.0:
            reliability = "Media (Condiciones Variables)"
        else:
            reliability = "Baja (Alta Incertidumbre en Tráfico)"

        return BayesianPrediction(
            mean_travel_time=y_mean,
            epistemic_uncertainty=np.sqrt(var_epistemic),
            aleatoric_uncertainty=np.sqrt(var_aleatoric),
            total_std=total_std,
            credible_interval_95=(ci_lower, ci_upper),
            reliability_level=reliability,
        )

    def sample_weights_posterior(self, n_samples: int = 500) -> np.ndarray:
        """Muestrea coeficientes beta desde la distribución a posteriori multivariante N(mu_N, Sigma_N)."""
        if self.mu_N is None or self.Sigma_N is None:
            raise ValueError("El modelo debe estar entrenado.")
        return np.random.multivariate_normal(mean=self.mu_N, cov=self.Sigma_N, size=n_samples)
