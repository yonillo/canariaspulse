"""Script y suite de verificación de integración del pipeline completo de GlobalPulse."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import pytest

from src.core_stats.distributions import (
    compute_confidence_intervals,
    compute_descriptive_stats,
    fit_continuous_distributions,
    fit_poisson_passenger_arrival
)
from src.core_stats.hypothesis_testing import (
    evaluate_corridors_anova,
    evaluate_normality,
    evaluate_two_groups_difference,
    evaluate_chi2_contingency
)
from src.core_stats.linear_regression import fit_travel_time_ols
from src.bayesian.conjugates import update_ontime_rate_beta_binomial
from src.bayesian.bayesian_regression import BayesianLinearRegressor
from src.bayesian.clustering_gmm import fit_gmm_stop_clustering
from src.bayesian.bayesian_network import GranCanariaBayesianNetwork
from src.data_ingestion.extract_network import get_curated_network


def test_full_data_science_pipeline():
    data_path = ROOT_DIR / "data" / "processed" / "telemetry_operations.parquet"
    assert data_path.exists(), f"No se encontró el fichero {data_path}"
    df = pd.read_parquet(data_path)
    assert len(df) > 0

    # 1. Test Distribuciones y Descriptiva
    desc = compute_descriptive_stats(df["actual_duration_min"])
    assert desc["mean"] > 0

    fits = fit_continuous_distributions(df["delay_min"])
    assert len(fits) > 0
    assert fits[0].dist_name == "Log-Normal"

    ci = compute_confidence_intervals(df["actual_duration_min"])
    assert ci["ci_mean_t"][0] < desc["mean"] < ci["ci_mean_t"][1]

    poisson_fit = fit_poisson_passenger_arrival(df["passengers_onboard"])
    assert poisson_fit["lambda_mle"] > 0

    # 2. Test Contrastes de Hipótesis
    norm_res = evaluate_normality(df["delay_min"])
    assert norm_res.reject_null is True

    week_vs_end = evaluate_two_groups_difference(
        df[df["is_weekend"] == 0]["delay_min"],
        df[df["is_weekend"] == 1]["delay_min"],
        name_a="Laborable",
        name_b="Fin de Semana"
    )
    assert week_vs_end["welch_t_test"].reject_null is True

    anova_res = evaluate_corridors_anova(df, value_col="delay_min", group_col="corridor")
    assert anova_res["anova_f_test"]["f_statistic"] > 0

    chi2_res = evaluate_chi2_contingency(df, row_col="is_peak", col_col="status")
    assert chi2_res.reject_null is True

    # 3. Test Regresión OLS y Gauss-Markov
    ols_bundle, _ = fit_travel_time_ols(df)
    assert ols_bundle.r_squared > 0.70

    # 4. Test Inferencia Bayesiana
    ontime_count = int((df["status"] == "A tiempo").sum())
    total_trips = len(df)
    beta_post = update_ontime_rate_beta_binomial(ontime_count, total_trips)
    assert 0.0 < beta_post.mean < 1.0

    # Regresión Bayesiana
    feature_cols = ["distance_km", "elevation_gain_m", "is_peak", "is_weekend", "gc1_incident"]
    X = df[feature_cols].values
    y = df["actual_duration_min"].values
    bayes_reg = BayesianLinearRegressor().fit(X, y)
    sample_trip = [45.0, 50.0, 1, 0, 1]
    pred = bayes_reg.predict_with_uncertainty(sample_trip)
    assert pred.credible_interval_95[0] < pred.mean_travel_time < pred.credible_interval_95[1]

    # Red Bayesiana pgmpy
    bn = GranCanariaBayesianNetwork()
    res_normal = bn.query_probability(["Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"], evidence={"Incidente_GC1": "No"})
    res_incident = bn.query_probability(["Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"], evidence={"Incidente_GC1": "Si"})
    assert res_incident["Retraso_L30_Sur"]["Retraso"] > res_normal["Retraso_L30_Sur"]["Retraso"]


if __name__ == "__main__":
    test_full_data_science_pipeline()
    print(">>> PIPELINE COMPLETO VERIFICADO CON ÉXITO <<<")
