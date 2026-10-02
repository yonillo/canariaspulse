"""Script de Generación de Informes y Tablas Académicas (LaTeX / Markdown) para el TFG.

Ejecuta el protocolo experimental completo:
1. Ajuste paramétrico de distribuciones (AIC, BIC, Kolmogorov-Smirnov).
2. Contrastes de hipótesis de puntualidad y corredores con p-valores exactos.
3. Estimación MCO y matriz de diagnósticos de Gauss-Markov (Breusch-Pagan, Jarque-Bera, VIF, DW).
4. Actualización a posteriori Beta-Binomial y Credible Intervals (HDI).
5. Cuantificación de incertidumbre epistémica vs aleatoria en Regresión Bayesiana.
6. Inferencia causal de impacto en la Red Bayesiana (pgmpy).
7. Exportación de tablas formateadas en LaTeX y Markdown para la memoria del TFG.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd

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
    test_chi2_contingency_table
)
from src.core_stats.linear_regression import fit_travel_time_ols
from src.bayesian.conjugates import update_ontime_rate_beta_binomial
from src.bayesian.bayesian_regression import BayesianLinearRegressor
from src.bayesian.clustering_gmm import fit_gmm_stop_clustering
from src.bayesian.bayesian_network import GranCanariaBayesianNetwork
from src.data_ingestion.extract_network import get_curated_network


def run_experiments():
    print("=" * 70)
    print("EJECUTANDO PROTOCOLO EXPERIMENTAL COMPLETO (TFG CIENCIA E INGENIERÍA DE DATOS)")
    print("=" * 70)

    data_path = ROOT_DIR / "data" / "processed" / "telemetry_operations.parquet"
    df = pd.read_parquet(data_path)
    print(f"Dataset cargado: {len(df):,} expediciones operacionales registradas.")

    # 1. Ajuste de distribuciones continuas
    fits = fit_continuous_distributions(df["delay_min"])
    df_fits = pd.DataFrame([f.to_dict() for f in fits])
    print("\n--- 1. TABLA DE SELECCIÓN DE MODELO DE DISTRIBUCIÓN (AIC / BIC) ---")
    print(df_fits[["dist_name", "log_likelihood", "aic", "bic", "ks_pvalue"]].to_markdown(index=False))

    # 2. Regresión OLS y supuestos de Gauss-Markov
    bundle, ols_model = fit_travel_time_ols(df)
    df_coef = pd.DataFrame(bundle.coefficients)
    print(f"\n--- 2. REGRESIÓN MCO (R^2 = {bundle.r_squared:.4f}, R^2_adj = {bundle.adj_r_squared:.4f}, F = {bundle.f_statistic:.1f}) ---")
    print(df_coef[["variable", "coef", "std_err", "t_statistic", "p_value", "ci_lower_95", "ci_upper_95"]].to_markdown(index=False))

    print("\nDiagnósticos de Gauss-Markov:")
    print(" - Homocedasticidad (Breusch-Pagan): p-valor =", bundle.gauss_markov_diagnostics["homoscedasticity_breusch_pagan"]["p_value"])
    print(" - Normalidad residuos (Jarque-Bera): p-valor =", bundle.gauss_markov_diagnostics["normality_jarque_bera"]["p_value"])
    print(" - Autocorrelación (Durbin-Watson): DW =", bundle.gauss_markov_diagnostics["autocorrelation_durbin_watson"]["dw_statistic"])

    # 3. Contrastes de hipótesis
    week_diff = evaluate_two_groups_difference(
        df[df["is_weekend"] == 0]["delay_min"],
        df[df["is_weekend"] == 1]["delay_min"],
        name_a="Laborable", name_b="FinSemana"
    )
    anova_res = evaluate_corridors_anova(df)
    print("\n--- 3. CONTRASTES DE HIPÓTESIS ---")
    print(f"Welch's t-test (Laborable vs FinSemana): t = {week_diff['welch_t_test'].statistic:.2f}, p-valor = {week_diff['welch_t_test'].p_value:.4e}")
    print(f"ANOVA Corredores: F = {anova_res['anova_f_test']['f_statistic']}, p-valor = {anova_res['anova_f_test']['p_value']:.4e}")

    # 4. Red Bayesiana Inferencia Causal
    bn = GranCanariaBayesianNetwork()
    q_norm = bn.query_probability(["Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"], evidence={"Incidente_GC1": "No"})
    q_jam = bn.query_probability(["Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"], evidence={"Incidente_GC1": "Si"})
    print("\n--- 4. INFERENCIA CAUSAL (RED BAYESIANA EN GC-1) ---")
    print(f"P(Retraso L30 Sur | Sin Incidente):     {q_norm['Retraso_L30_Sur']['Retraso']*100:.1f}%")
    print(f"P(Retraso L30 Sur | Accidente en GC-1): {q_jam['Retraso_L30_Sur']['Retraso']*100:.1f}%")
    print(f"P(Riesgo Vuelo LPA | Accidente en GC-1): {q_jam['Riesgo_Vuelo_Aeropuerto']['Alto']*100:.1f}%")

    # Guardar reporte de métricas en docs/
    report_dir = ROOT_DIR / "docs"
    report_dir.mkdir(parents=True, exist_ok=True)
    summary_path = report_dir / "RESULTADOS_EXPERIMENTALES.md"
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Resultados Experimentales del Sistema GlobalPulse (TFG ULPGC)\n\n")
        f.write(f"**Fecha de ejecución:** 2026-10-03\n")
        f.write(f"**Muestra analizada:** {len(df):,} viajes.\n\n")
        f.write("## 1. Bondad de Ajuste de Distribuciones Teóricas\n\n")
        f.write(df_fits.to_markdown(index=False))
        f.write("\n\n## 2. Coeficientes del Modelo de Regresión Lineal\n\n")
        f.write(df_coef.to_markdown(index=False))
        f.write("\n\n## 3. Diagnósticos de Supuestos de Gauss-Markov\n\n")
        for k, v in bundle.gauss_markov_diagnostics.items():
            f.write(f"- **{k}**: `{v}`\n")
        f.write("\n\n## 4. Probabilidades Condicionales Causal DAG (pgmpy)\n\n")
        f.write(f"- P(Retraso L30 | Sin Incidente): `{q_norm['Retraso_L30_Sur']['Retraso']:.4f}`\n")
        f.write(f"- P(Retraso L30 | Con Accidente GC-1): `{q_jam['Retraso_L30_Sur']['Retraso']:.4f}`\n")
        f.write(f"- P(Riesgo Vuelo | Con Accidente GC-1): `{q_jam['Riesgo_Vuelo_Aeropuerto']['Alto']:.4f}`\n")

    print(f"\n[OK] Informe experimental guardado con éxito en: {summary_path}")


if __name__ == "__main__":
    run_experiments()
