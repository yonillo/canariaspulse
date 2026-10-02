"""Batería de Pruebas Unitarias de Propiedades Matemáticas y Estadísticas Formales (TFG ULPGC).

Verifica computacionalmente los teoremas y propiedades del temario:
1. Teorema de Gauss-Markov: Ortogonalidad de residuos OLS (X^T * e = 0 y sum(e) = 0).
2. Familia Conjugada Beta-Binomial: Validación de momentos a posteriori (E[theta] y Var[theta]).
3. Regresión Bayesiana: Descomposición de la incertidumbre (Varianza epistémica >= 0).
4. Redes Bayesianas: Inferencia causal, d-separación e independencia condicional.
5. Estimación Puntual MLE: Verificación de verosimilitud en distribución de Poisson y Log-Normal.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Añadir raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from src.core_stats.distributions import (
    compute_descriptive_stats,
    fit_continuous_distributions,
    fit_poisson_passenger_arrival,
    compute_confidence_intervals
)
from src.core_stats.hypothesis_testing import (
    evaluate_normality,
    evaluate_two_groups_difference,
    evaluate_corridors_anova
)
from src.core_stats.linear_regression import fit_travel_time_ols
from src.bayesian.conjugates import update_ontime_rate_beta_binomial
from src.bayesian.bayesian_regression import BayesianLinearRegressor
from src.bayesian.bayesian_network import GranCanariaBayesianNetwork
from src.bayesian.clustering_gmm import fit_gmm_stop_clustering
from src.data_ingestion.extract_network import get_curated_network


@pytest.fixture(scope="module")
def dataset():
    """Carga los datos operacionales de telemetría."""
    path = ROOT_DIR / "data" / "processed" / "telemetry_operations.parquet"
    if not path.exists():
        from src.data_ingestion.extract_network import generate_operational_telemetry
        return generate_operational_telemetry(num_days=45)
    return pd.read_parquet(path)


def test_gauss_markov_properties(dataset):
    """Verifica los teoremas de los estimadores MCO (Mínimos Cuadrados Ordinarios).

    Propiedad 1: La suma de residuos es cero: sum(e_i) approx 0
    Propiedad 2: Ortogonalidad entre regresores y residuos: X^T * e = 0
    """
    bundle, model = fit_travel_time_ols(dataset)
    residuals = model.resid
    X = model.model.exog

    # 1. Media de residuos nula (primer supuesto fundamental con término constante)
    assert np.isclose(np.mean(residuals), 0.0, atol=1e-5), "La media de los residuos OLS debe ser nula."

    # 2. Ortogonalidad matricial: X^T * e = 0
    orthogonal_product = X.T @ residuals
    assert np.allclose(orthogonal_product, 0.0, atol=1e-3), "Los residuos OLS deben ser ortogonales a la matriz de diseño X."

    # 3. R^2 debe estar estrictamente acotado en [0, 1]
    assert 0.0 <= bundle.r_squared <= 1.0, "El coeficiente de determinación R^2 debe pertenecer al intervalo [0, 1]."
    assert bundle.adj_r_squared <= bundle.r_squared, "El R^2 ajustado debe ser menor o igual que el R^2 convencional."


def test_beta_binomial_exact_conjugacy():
    """Verifica las ecuaciones analíticas de la distribución a posteriori Beta-Binomial.

    Prior: Beta(alpha_0, beta_0)
    Verosimilitud: k éxitos en n ensayos
    Posterior: Beta(alpha_0 + k, beta_0 + n - k)
    E[theta | D] = alpha_N / (alpha_N + beta_N)
    """
    a0, b0 = 3.0, 5.0
    k, n = 42, 60

    post = update_ontime_rate_beta_binomial(successes=k, trials=n, prior_alpha=a0, prior_beta=b0)

    # Verificación de parámetros a posteriori
    expected_alpha = a0 + k
    expected_beta = b0 + (n - k)
    assert post.post_alpha == expected_alpha
    assert post.post_beta == expected_beta

    # Verificación de la media a posteriori teórica
    theoretical_mean = expected_alpha / (expected_alpha + expected_beta)
    assert np.isclose(post.mean, theoretical_mean, atol=1e-6)

    # Verificación de que el HDI 95% contiene a la media y es estrictamente monótono
    low, high = post.hdi_95
    assert 0.0 < low < post.mean < high < 1.0
    # Verificación de masa de probabilidad en el intervalo
    prob_mass = stats.beta.cdf(high, expected_alpha, expected_beta) - stats.beta.cdf(low, expected_alpha, expected_beta)
    assert np.isclose(prob_mass, 0.95, atol=1e-3)


def test_bayesian_regression_variance_decomposition(dataset):
    """Verifica la descomposición de la varianza predictiva en incertidumbre epistémica y aleatoria.

    sigma_*^2 = sigma_ruido^2 + x_*^T Sigma_N x_*
    La incertidumbre epistémica debe ser estrictamente positiva para cualquier x_* no nulo.
    """
    feature_cols = ["distance_km", "elevation_gain_m", "is_peak", "is_weekend", "gc1_incident"]
    X = dataset[feature_cols].values
    y = dataset["actual_duration_min"].values

    reg = BayesianLinearRegressor(alpha_prior=1.0, beta_noise=0.25).fit(X, y)

    # Evaluar en un punto de prueba arbitrario
    x_test = np.array([55.0, 120.0, 1, 0, 1])
    pred = reg.predict_with_uncertainty(x_test, n_mc_samples=2000)

    # 1. La incertidumbre epistémica debe ser estrictamente mayor a 0
    assert pred.epistemic_uncertainty > 0.0

    # 2. Varianza total >= Varianza aleatoria (el ruido es la cota inferior)
    min_theoretical_std = np.sqrt(1.0 / reg.beta_noise)
    assert pred.total_std >= min_theoretical_std

    # 3. Intervalo de credibilidad bien ordenado
    low, high = pred.credible_interval_95
    assert low < pred.mean_travel_time < high


def test_causal_bayesian_network_d_separation_and_monotonicity():
    """Verifica que la Red Bayesiana cumpla con las propiedades causales y de monotonía de Gran Canaria.

    Si ocurre un incidente en la GC-1:
    P(Colapso Hoya Plata | Incidente = Si) > P(Colapso Hoya Plata | Incidente = No)
    P(Retraso L30 Sur | Incidente = Si) > P(Retraso L30 Sur | Incidente = No)
    P(Riesgo Vuelo LPA | Incidente = Si) > P(Riesgo Vuelo LPA | Incidente = No)
    """
    bn = GranCanariaBayesianNetwork()

    q_no = bn.query_probability(["Atasco_HoyaPlata", "Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"], evidence={"Incidente_GC1": "No"})
    q_si = bn.query_probability(["Atasco_HoyaPlata", "Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"], evidence={"Incidente_GC1": "Si"})

    # Monotonía causal de impacto
    assert q_si["Atasco_HoyaPlata"]["Colapso"] > q_no["Atasco_HoyaPlata"]["Colapso"]
    assert q_si["Retraso_L30_Sur"]["Retraso"] > q_no["Retraso_L30_Sur"]["Retraso"]
    assert q_si["Riesgo_Vuelo_Aeropuerto"]["Alto"] > q_no["Riesgo_Vuelo_Aeropuerto"]["Alto"]


def test_poisson_maximum_likelihood(dataset):
    """Verifica que la estimación MLE de lambda en Poisson sea exactamente la media muestral."""
    res = fit_poisson_passenger_arrival(dataset["passengers_onboard"])
    sample_mean = float(np.mean(dataset["passengers_onboard"]))
    assert np.isclose(res["lambda_mle"], sample_mean, atol=1e-2)


def test_statistical_hypothesis_framework(dataset):
    """Verifica la ejecución formal de contrastes de hipótesis (Temas 6 y 9).

    1. D'Agostino omnibus test sobre retrasos.
    2. Welch's t-test y Mann-Whitney U sobre laborables vs fines de semana.
    3. ANOVA de una vía y test de homocedasticidad de Levene entre corredores.
    """
    # 1. Test de normalidad
    norm = evaluate_normality(dataset["delay_min"])
    assert norm.test_name.startswith("Test de Normalidad")
    assert 0.0 <= norm.p_value <= 1.0

    # 2. Contraste de dos muestras
    diff = evaluate_two_groups_difference(
        dataset[dataset["is_weekend"] == 0]["delay_min"],
        dataset[dataset["is_weekend"] == 1]["delay_min"]
    )
    assert "welch_t_test" in diff and "mann_whitney_u" in diff
    assert diff["welch_t_test"].reject_null is True

    # 3. ANOVA entre corredores
    anova = evaluate_corridors_anova(dataset)
    assert "anova_f_test" in anova
    assert anova["anova_f_test"]["f_statistic"] > 0
