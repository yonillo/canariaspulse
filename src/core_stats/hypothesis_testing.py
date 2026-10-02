"""Módulo de Contrastes de Hipótesis y Tests de Significancia Estadística (Tema 9 y Bloque 2 Tema 0).

Implementa:
- Tests de normalidad (D'Agostino-Pearson y Shapiro-Wilk).
- Contrastes de 2 muestras paramétricos (Welch's t-test) y no paramétricos (Mann-Whitney U).
- Análisis de Varianza (ANOVA F-test) y Kruskal-Wallis entre múltiples corredores.
- Test de igualdad de varianzas (Levene test).
- Test Chi-cuadrado de independencia para puntualidad según franja horaria.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class HypothesisTestResult:
    test_name: str
    null_hypothesis: str
    alternative_hypothesis: str
    statistic: float
    p_value: float
    alpha: float = 0.05
    reject_null: bool = False
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "null_hypothesis": self.null_hypothesis,
            "alternative_hypothesis": self.alternative_hypothesis,
            "statistic": round(self.statistic, 4),
            "p_value": float(f"{self.p_value:.4e}" if self.p_value < 1e-4 else round(self.p_value, 4)),
            "alpha": self.alpha,
            "reject_null": self.reject_null,
            "interpretation": self.interpretation,
        }


def evaluate_normality(data: pd.Series | np.ndarray, alpha: float = 0.05) -> HypothesisTestResult:
    """Evalúa la normalidad de la variable mediante el test de D'Agostino-Pearson (omnibus de asimetría y curtosis)."""
    clean = np.asarray(data, dtype=float)
    clean = clean[~np.isnan(clean)]

    stat, pval = stats.normaltest(clean)
    reject = bool(pval < alpha)
    interp = (
        f"Se rechaza H0 (p < {alpha}). La distribución difiere significativamente de una distribución Normal."
        if reject
        else f"No se rechaza H0 (p >= {alpha}). No hay evidencia suficiente para descartar normalidad."
    )

    return HypothesisTestResult(
        test_name="Test de Normalidad D'Agostino-Pearson",
        null_hypothesis="La muestra proviene de una distribución Normal",
        alternative_hypothesis="La muestra no proviene de una distribución Normal",
        statistic=float(stat),
        p_value=float(pval),
        alpha=alpha,
        reject_null=reject,
        interpretation=interp,
    )


# Alias de compatibilidad
test_normality = evaluate_normality


def evaluate_two_groups_difference(
    group_a: pd.Series | np.ndarray,
    group_b: pd.Series | np.ndarray,
    name_a: str = "Grupo A",
    name_b: str = "Grupo B",
    alpha: float = 0.05
) -> Dict[str, HypothesisTestResult]:
    """Realiza contraste de dos muestras independientes para comprobar si hay diferencias en la media o mediana."""
    clean_a = np.asarray(group_a, dtype=float)
    clean_a = clean_a[~np.isnan(clean_a)]
    clean_b = np.asarray(group_b, dtype=float)
    clean_b = clean_b[~np.isnan(clean_b)]

    # 1. Welch's t-test (no asume varianzas iguales)
    t_stat, t_pval = stats.ttest_ind(clean_a, clean_b, equal_var=False)
    reject_t = bool(t_pval < alpha)
    interp_t = (
        f"Diferencia estadísticamente significativa entre las medias de {name_a} (media={np.mean(clean_a):.2f}) "
        f"y {name_b} (media={np.mean(clean_b):.2f}) con p-valor={t_pval:.4e}."
        if reject_t
        else f"No existe diferencia estadísticamente significativa en las medias (p={t_pval:.4f} >= {alpha})."
    )
    t_res = HypothesisTestResult(
        test_name="Welch's t-test (Medias independientes)",
        null_hypothesis=f"Media({name_a}) == Media({name_b})",
        alternative_hypothesis=f"Media({name_a}) != Media({name_b})",
        statistic=float(t_stat),
        p_value=float(t_pval),
        alpha=alpha,
        reject_null=reject_t,
        interpretation=interp_t,
    )

    # 2. Mann-Whitney U (robusto a distribuciones no normales y colas pesadas)
    u_stat, u_pval = stats.mannwhitneyu(clean_a, clean_b, alternative="two-sided")
    reject_u = bool(u_pval < alpha)
    interp_u = (
        f"La distribución de rangos/medianas de {name_a} y {name_b} difiere con significancia estadística (p={u_pval:.4e})."
        if reject_u
        else f"No se detecta desplazamiento estocástico significativo entre ambos grupos (p={u_pval:.4f})."
    )
    u_res = HypothesisTestResult(
        test_name="Mann-Whitney U Test (No paramétrico)",
        null_hypothesis=f"Distribución({name_a}) == Distribución({name_b})",
        alternative_hypothesis=f"Distribución({name_a}) != Distribución({name_b})",
        statistic=float(u_stat),
        p_value=float(u_pval),
        alpha=alpha,
        reject_null=reject_u,
        interpretation=interp_u,
    )

    return {"welch_t_test": t_res, "mann_whitney_u": u_res}


test_two_groups_difference = evaluate_two_groups_difference


def evaluate_corridors_anova(
    df: pd.DataFrame,
    value_col: str = "delay_min",
    group_col: str = "corridor",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Realiza un ANOVA de una vía y Kruskal-Wallis para comparar el retraso entre los corredores de la isla."""
    groups = [group[value_col].dropna().values for _, group in df.groupby(group_col)]
    group_names = [str(name) for name, _ in df.groupby(group_col)]

    if len(groups) < 2:
        return {}

    # Test de Levene de homocedasticidad
    levene_stat, levene_pval = stats.levene(*groups)

    # ANOVA de 1 vía
    f_stat, f_pval = stats.f_oneway(*groups)
    reject_anova = bool(f_pval < alpha)

    # Kruskal-Wallis (alternativa no paramétrica)
    kw_stat, kw_pval = stats.kruskal(*groups)
    reject_kw = bool(kw_pval < alpha)

    summary_by_group = df.groupby(group_col)[value_col].agg(["count", "mean", "std", "median"]).reset_index()

    return {
        "group_names": group_names,
        "summary": summary_by_group.to_dict(orient="records"),
        "levene_homoscedasticity": {
            "statistic": round(float(levene_stat), 4),
            "p_value": float(levene_pval),
            "equal_variance": bool(levene_pval >= alpha),
        },
        "anova_f_test": {
            "f_statistic": round(float(f_stat), 4),
            "p_value": float(f_pval),
            "reject_null": reject_anova,
            "conclusion": "Existen diferencias significativas de retraso entre corredores" if reject_anova else "No se observan diferencias significativas entre corredores",
        },
        "kruskal_wallis_test": {
            "h_statistic": round(float(kw_stat), 4),
            "p_value": float(kw_pval),
            "reject_null": reject_kw,
            "conclusion": "Diferencia estadísticamente significativa en rangos de retraso entre corredores" if reject_kw else "Sin diferencias de rango",
        }
    }


test_corridors_anova = evaluate_corridors_anova


def test_chi2_contingency_table(
    df: pd.DataFrame,
    row_col: str = "is_peak",
    col_col: str = "status",
    alpha: float = 0.05
) -> HypothesisTestResult:
    """Test Chi-cuadrado de independencia para tablas de contingencia (ej. puntualidad vs hora punta)."""
    contingency = pd.crosstab(df[row_col], df[col_col])
    chi2_stat, p_val, dof, expected = stats.chi2_contingency(contingency)

    reject = bool(p_val < alpha)
    interp = (
        f"Se rechaza H0 de independencia (Chi2={chi2_stat:.2f}, dof={dof}, p={p_val:.4e}). "
        f"La puntualidad está significativamente condicionada por {row_col}."
        if reject
        else "No hay evidencia de dependencia estadística entre ambas variables."
    )

    return HypothesisTestResult(
        test_name="Test Chi-cuadrado de Independencia",
        null_hypothesis=f"Las variables '{row_col}' y '{col_col}' son independientes",
        alternative_hypothesis=f"Existe asociación estadística entre '{row_col}' y '{col_col}'",
        statistic=float(chi2_stat),
        p_value=float(p_val),
        alpha=alpha,
        reject_null=reject,
        interpretation=interp,
    )


evaluate_chi2_contingency = test_chi2_contingency_table
