"""Módulo del Modelo de Regresión Lineal y Diagnósticos de Gauss-Markov (Tema 10).

Implementa:
- Ajuste por Mínimos Cuadrados Ordinarios (OLS) para el tiempo de viaje real.
- Diagnóstico exhaustivo de supuestos de Gauss-Markov:
  * Homocedasticidad (Test de Breusch-Pagan).
  * Normalidad de residuos (Jarque-Bera y Omnibus).
  * Multicolinealidad (Variance Inflation Factor - VIF).
  * Autocorrelación de errores (Estadístico de Durbin-Watson).
- Desglose de coeficientes, errores estándar e intervalos de confianza del 95%.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson


@dataclass
class RegressionResultsBundle:
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_pvalue: float
    aic: float
    bic: float
    coefficients: List[Dict[str, Any]]
    gauss_markov_diagnostics: Dict[str, Any]
    formula: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formula": self.formula,
            "r_squared": round(self.r_squared, 4),
            "adj_r_squared": round(self.adj_r_squared, 4),
            "f_statistic": round(self.f_statistic, 2),
            "f_pvalue": float(f"{self.f_pvalue:.4e}"),
            "aic": round(self.aic, 2),
            "bic": round(self.bic, 2),
            "coefficients": self.coefficients,
            "gauss_markov_diagnostics": self.gauss_markov_diagnostics,
        }


def fit_travel_time_ols(
    df: pd.DataFrame,
    target_col: str = "actual_duration_min",
    feature_cols: Optional[List[str]] = None
) -> Tuple[RegressionResultsBundle, sm.regression.linear_model.RegressionResultsWrapper]:
    """Ajusta un modelo OLS para estimar la duración del trayecto en función de la topografía y tráfico."""
    if feature_cols is None:
        feature_cols = [
            "distance_km",
            "elevation_gain_m",
            "is_peak",
            "is_weekend",
            "gc1_incident"
        ]

    # Preparamos variables numéricas
    clean_df = df[[target_col] + feature_cols].dropna().copy()
    y = clean_df[target_col]
    X = clean_df[feature_cols]
    X_with_const = sm.add_constant(X)

    model = sm.OLS(y, X_with_const).fit()

    # 1. Coeficientes e intervalos de confianza
    conf_int = model.conf_int()
    coef_list = []
    for var_name in X_with_const.columns:
        coef_list.append({
            "variable": var_name,
            "coef": round(float(model.params[var_name]), 4),
            "std_err": round(float(model.bse[var_name]), 4),
            "t_statistic": round(float(model.tvalues[var_name]), 3),
            "p_value": float(f"{model.pvalues[var_name]:.4e}"),
            "ci_lower_95": round(float(conf_int.loc[var_name, 0]), 4),
            "ci_upper_95": round(float(conf_int.loc[var_name, 1]), 4),
        })

    # 2. Diagnóstico de Gauss-Markov
    residuals = model.resid

    # A) Homocedasticidad (Breusch-Pagan)
    bp_stat, bp_pval, _, _ = het_breuschpagan(residuals, model.model.exog)

    # B) Normalidad de residuos (Jarque-Bera)
    jb_stat, jb_pval, skew, kurt = sm.stats.stattools.jarque_bera(residuals)

    # C) Autocorrelación (Durbin-Watson, ideal ~ 2.0)
    dw_stat = durbin_watson(residuals)

    # D) Factores de Inflación de la Varianza (VIF) para multicolinealidad
    vif_records = []
    for i, col in enumerate(X_with_const.columns):
        if col == "const":
            continue
        vif_val = variance_inflation_factor(X_with_const.values, i)
        vif_records.append({
            "variable": col,
            "vif": round(float(vif_val), 2),
            "multicollinearity_risk": "Alto (>5)" if vif_val > 5.0 else "Aceptable (<5)",
        })

    diagnostics = {
        "homoscedasticity_breusch_pagan": {
            "lm_statistic": round(float(bp_stat), 2),
            "p_value": float(bp_pval),
            "homoscedastic": bool(bp_pval >= 0.05),
            "note": "Residuos con varianza constante (Homocedásticos)" if bp_pval >= 0.05 else "Heterocedasticidad presente (típica en tráfico congestionado)"
        },
        "normality_jarque_bera": {
            "jb_statistic": round(float(jb_stat), 2),
            "p_value": float(jb_pval),
            "normal_residuals": bool(jb_pval >= 0.05),
            "skewness": round(float(skew), 3),
            "kurtosis": round(float(kurt), 3),
        },
        "autocorrelation_durbin_watson": {
            "dw_statistic": round(float(dw_stat), 3),
            "interpretation": "Sin autocorrelación serial de primer orden (próximo a 2)" if 1.5 <= dw_stat <= 2.5 else "Posible correlación en residuos",
        },
        "multicollinearity_vif": vif_records,
    }

    formula_str = f"{target_col} ~ " + " + ".join(feature_cols)

    bundle = RegressionResultsBundle(
        r_squared=float(model.rsquared),
        adj_r_squared=float(model.rsquared_adj),
        f_statistic=float(model.fvalue),
        f_pvalue=float(model.f_pvalue),
        aic=float(model.aic),
        bic=float(model.bic),
        coefficients=coef_list,
        gauss_markov_diagnostics=diagnostics,
        formula=formula_str,
    )

    return bundle, model
