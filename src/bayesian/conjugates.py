"""Módulo de Estimación Bayesiana Exacta con Familias Conjugadas (Bloque 2 Tema 2).

Implementa:
- Modelo conjugado Beta-Binomial para la probabilidad de puntualidad theta de una línea o parada.
  Prior: theta ~ Beta(alpha_0, beta_0)
  Verosimilitud: k ~ Binomial(n, theta)
  Posterior: theta | D ~ Beta(alpha_0 + k, beta_0 + n - k)
- Cálculo analítico de la media a posteriori, varianza y el Highest Density Interval (HDI) del 95%.
- Actualización secuencial online día a día conforme se registran nuevas observaciones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import stats


@dataclass
class BetaBinomialPosterior:
    prior_alpha: float
    prior_beta: float
    successes: int
    trials: int
    post_alpha: float
    post_beta: float
    mean: float
    mode: float
    variance: float
    hdi_95: Tuple[float, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prior_alpha": self.prior_alpha,
            "prior_beta": self.prior_beta,
            "successes_ontime": self.successes,
            "trials_total": self.trials,
            "post_alpha": round(self.post_alpha, 2),
            "post_beta": round(self.post_beta, 2),
            "posterior_mean_prob": round(self.mean, 4),
            "posterior_mode_prob": round(self.mode, 4),
            "posterior_variance": round(self.variance, 6),
            "hdi_95": (round(self.hdi_95[0], 4), round(self.hdi_95[1], 4)),
        }


def update_ontime_rate_beta_binomial(
    successes: int,
    trials: int,
    prior_alpha: float = 2.0,
    prior_beta: float = 2.0,
    confidence: float = 0.95
) -> BetaBinomialPosterior:
    """Actualiza la distribución a posteriori analítica de la tasa de puntualidad con modelo Beta-Binomial."""
    post_alpha = prior_alpha + successes
    post_beta = prior_beta + (trials - successes)

    # Media a posteriori: E[theta] = alpha / (alpha + beta)
    mean = post_alpha / (post_alpha + post_beta)

    # Moda a posteriori (si alpha, beta > 1)
    if post_alpha > 1 and post_beta > 1:
        mode = (post_alpha - 1.0) / (post_alpha + post_beta - 2.0)
    else:
        mode = mean

    # Varianza a posteriori
    var = (post_alpha * post_beta) / (((post_alpha + post_beta) ** 2) * (post_alpha + post_beta + 1.0))

    # Intervalo de Credibilidad (HDI) simétrico en colas (Equal-tailed interval)
    alpha_tail = (1.0 - confidence) / 2.0
    lower = float(stats.beta.ppf(alpha_tail, post_alpha, post_beta))
    upper = float(stats.beta.ppf(1.0 - alpha_tail, post_alpha, post_beta))

    return BetaBinomialPosterior(
        prior_alpha=prior_alpha,
        prior_beta=prior_beta,
        successes=successes,
        trials=trials,
        post_alpha=post_alpha,
        post_beta=post_beta,
        mean=float(mean),
        mode=float(mode),
        variance=float(var),
        hdi_95=(lower, upper),
    )


def compute_beta_pdf_curve(alpha: float, beta: float, n_points: int = 200) -> Tuple[np.ndarray, np.ndarray]:
    """Genera la curva de densidad para graficar la distribución a priori o a posteriori."""
    x = np.linspace(0.001, 0.999, n_points)
    y = stats.beta.pdf(x, alpha, beta)
    return x, y
