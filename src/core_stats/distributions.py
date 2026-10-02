"""Módulo de Distribuciones y Estimación Paramétrica (Temas 1, 3, 4, 7 y 8).

Implementa:
- Estadística descriptiva exhaustiva (asimetría, curtosis, IQR).
- Estimación paramétrica puntual por Máxima Verosimilitud (MLE) para Log-Normal, Gamma, Weibull y Normal.
- Comparación de bondad de ajuste mediante AIC (Akaike Information Criterion) y BIC.
- Intervalos de confianza paramétricos y bootstrap para la media y percentiles (Theme 8).
- Modelado discreto de Poisson para afluencia de pasajeros (Theme 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class DistributionFitResult:
    dist_name: str
    params: Tuple[float, ...]
    log_likelihood: float
    aic: float
    bic: float
    ks_statistic: float
    ks_pvalue: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dist_name": self.dist_name,
            "params": [round(p, 4) for p in self.params],
            "log_likelihood": round(self.log_likelihood, 2),
            "aic": round(self.aic, 2),
            "bic": round(self.bic, 2),
            "ks_statistic": round(self.ks_statistic, 4),
            "ks_pvalue": round(self.ks_pvalue, 4),
        }


def compute_descriptive_stats(series: pd.Series | np.ndarray) -> Dict[str, float]:
    """Calcula estadísticos descriptivos completos (Tema 1)."""
    clean = np.asarray(series)
    clean = clean[~np.isnan(clean)]

    n = len(clean)
    mean = float(np.mean(clean))
    median = float(np.median(clean))
    std = float(np.std(clean, ddof=1)) if n > 1 else 0.0
    var = float(np.var(clean, ddof=1)) if n > 1 else 0.0
    q25 = float(np.percentile(clean, 25))
    q75 = float(np.percentile(clean, 75))
    iqr = q75 - q25
    skewness = float(stats.skew(clean))
    kurt = float(stats.kurtosis(clean))  # Exceso de curtosis (0 para Normal)

    return {
        "n_samples": n,
        "mean": round(mean, 2),
        "median": round(median, 2),
        "std": round(std, 2),
        "var": round(var, 2),
        "iqr": round(iqr, 2),
        "p25": round(q25, 2),
        "p75": round(q75, 2),
        "p95": round(float(np.percentile(clean, 95)), 2),
        "skewness": round(skewness, 3),
        "kurtosis": round(kurt, 3),
    }


def fit_continuous_distributions(
    data: pd.Series | np.ndarray,
    candidate_dists: Optional[List[str]] = None
) -> List[DistributionFitResult]:
    """Ajusta distribuciones continuas por Máxima Verosimilitud (MLE) (Tema 4 y 7).

    Compara Log-Normal, Gamma, Weibull y Normal, calculando AIC y BIC para selección de modelo.
    """
    clean = np.asarray(data, dtype=float)
    clean = clean[~np.isnan(clean)]
    # Para Log-Normal, Gamma y Weibull los datos deben ser estrictamente positivos
    # Si hay valores <= 0 (ej. retraso negativo o cero), aplicamos un desplazamiento mínimo
    min_val = np.min(clean)
    shift = 0.0
    if min_val <= 0:
        shift = abs(min_val) + 0.1
        clean = clean + shift

    n = len(clean)
    candidate_dists = candidate_dists or ["lognorm", "gamma", "weibull_min", "norm"]

    dist_map = {
        "lognorm": ("Log-Normal", stats.lognorm),
        "gamma": ("Gamma", stats.gamma),
        "weibull_min": ("Weibull", stats.weibull_min),
        "norm": ("Normal", stats.norm),
    }

    results = []
    for code, (label, dist_obj) in dist_map.items():
        if code not in candidate_dists:
            continue
        try:
            # Estimación puntual MLE
            params = dist_obj.fit(clean)
            # Log-verosimilitud
            ll = float(np.sum(dist_obj.logpdf(clean, *params)))
            k = len(params)
            aic = 2 * k - 2 * ll
            bic = k * np.log(n) - 2 * ll

            # Test de bondad de ajuste Kolmogorov-Smirnov
            ks_res = stats.kstest(clean, dist_obj.name, args=params)

            results.append(DistributionFitResult(
                dist_name=label,
                params=params,
                log_likelihood=ll,
                aic=aic,
                bic=bic,
                ks_statistic=float(ks_res.statistic),
                ks_pvalue=float(ks_res.pvalue),
            ))
        except Exception:
            continue

    # Ordenar por mejor AIC (menor valor = mejor ajuste)
    results.sort(key=lambda x: x.aic)
    return results


def compute_confidence_intervals(
    data: pd.Series | np.ndarray,
    confidence: float = 0.95
) -> Dict[str, Tuple[float, float]]:
    """Calcula intervalos de confianza para la media (t-Student y normal) y varianza (Chi-cuadrado) (Tema 8)."""
    clean = np.asarray(data, dtype=float)
    clean = clean[~np.isnan(clean)]
    n = len(clean)
    if n < 2:
        return {}

    mean = float(np.mean(clean))
    s = float(np.std(clean, ddof=1))
    alpha = 1.0 - confidence

    # 1. Intervalo de la media con t-Student (población normal, varianza desconocida)
    t_crit = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
    margin_t = t_crit * (s / np.sqrt(n))
    ci_mean_t = (round(mean - margin_t, 2), round(mean + margin_t, 2))

    # 2. Intervalo de la varianza con Chi-cuadrado: [(n-1)s^2 / chi_upper, (n-1)s^2 / chi_lower]
    chi2_lower = stats.chi2.ppf(alpha / 2.0, df=n - 1)
    chi2_upper = stats.chi2.ppf(1.0 - alpha / 2.0, df=n - 1)
    num = (n - 1) * (s ** 2)
    ci_var = (round(num / chi2_upper, 2), round(num / chi2_lower, 2))
    ci_std = (round(np.sqrt(ci_var[0]), 2), round(np.sqrt(ci_var[1]), 2))

    return {
        "ci_mean_t": ci_mean_t,
        "ci_variance_chi2": ci_var,
        "ci_std_chi2": ci_std,
    }


def fit_poisson_passenger_arrival(passengers_series: pd.Series | np.ndarray) -> Dict[str, Any]:
    """Ajuste de distribución discreta de Poisson para afluencia de pasajeros (Tema 3 y 7)."""
    clean = np.asarray(passengers_series, dtype=int)
    clean = clean[~np.isnan(clean)]
    n = len(clean)
    # Estimador MLE de lambda en Poisson es la media muestral
    lambda_mle = float(np.mean(clean))
    sample_var = float(np.var(clean, ddof=1))

    # Test de dispersión (si var > mean, hay sobredispersión -> Poisson vs Binomial Negativa)
    dispersion_ratio = sample_var / lambda_mle if lambda_mle > 0 else 1.0

    return {
        "n_trips": n,
        "lambda_mle": round(lambda_mle, 2),
        "sample_variance": round(sample_var, 2),
        "dispersion_ratio": round(dispersion_ratio, 2),
        "is_overdispersed": bool(dispersion_ratio > 1.25),
        "p_exceed_capacity_60": round(float(1.0 - stats.poisson.cdf(60, lambda_mle)), 4),
    }
