# Resultados Experimentales del Sistema GlobalPulse (TFG ULPGC)

**Fecha de ejecución:** 2026-10-03
**Muestra analizada:** 14,889 viajes.

## 1. Bondad de Ajuste de Distribuciones Teóricas

| dist_name   | params                                                         |   log_likelihood |    aic |    bic |   ks_statistic |   ks_pvalue |
|:------------|:---------------------------------------------------------------|-----------------:|-------:|-------:|---------------:|------------:|
| Log-Normal  | [np.float64(0.2282), -5.6996, np.float64(42.177)]              |         -54839.7 | 109685 | 109708 |         0.0666 |           0 |
| Gamma       | [np.float64(15.1037), np.float64(-1.2216), np.float64(2.5717)] |         -55067.5 | 110141 | 110164 |         0.0792 |           0 |
| Weibull     | [np.float64(3.447), np.float64(0.0651), np.float64(41.4744)]   |         -56859.6 | 113725 | 113748 |         0.1151 |           0 |

## 2. Coeficientes del Modelo de Regresión Lineal

| variable         |    coef |   std_err |   t_statistic |     p_value |   ci_lower_95 |   ci_upper_95 |
|:-----------------|--------:|----------:|--------------:|------------:|--------------:|--------------:|
| const            |  6.702  |    0.2717 |        24.663 | 1.1506e-131 |        6.1694 |        7.2347 |
| distance_km      |  1.0699 |    0.005  |       214.332 | 0           |        1.0602 |        1.0797 |
| elevation_gain_m |  0.0366 |    0.0004 |        86.694 | 0           |        0.0357 |        0.0374 |
| is_peak          | 10.5705 |    0.2052 |        51.504 | 0           |       10.1682 |       10.9728 |
| is_weekend       | -3.8945 |    0.2272 |       -17.138 | 3.2543e-65  |       -4.3399 |       -3.4491 |
| gc1_incident     |  9.8455 |    0.3846 |        25.597 | 1.8502e-141 |        9.0916 |       10.5994 |

## 3. Diagnósticos de Supuestos de Gauss-Markov

- **homoscedasticity_breusch_pagan**: `{'lm_statistic': 2396.07, 'p_value': 0.0, 'homoscedastic': False, 'note': 'Heterocedasticidad presente (típica en tráfico congestionado)'}`
- **normality_jarque_bera**: `{'jb_statistic': 3692.72, 'p_value': 0.0, 'normal_residuals': False, 'skewness': 0.75, 'kurtosis': 4.925}`
- **autocorrelation_durbin_watson**: `{'dw_statistic': 0.805, 'interpretation': 'Posible correlación en residuos'}`
- **multicollinearity_vif**: `[{'variable': 'distance_km', 'vif': 1.27, 'multicollinearity_risk': 'Aceptable (<5)'}, {'variable': 'elevation_gain_m', 'vif': 1.29, 'multicollinearity_risk': 'Aceptable (<5)'}, {'variable': 'is_peak', 'vif': 1.0, 'multicollinearity_risk': 'Aceptable (<5)'}, {'variable': 'is_weekend', 'vif': 1.03, 'multicollinearity_risk': 'Aceptable (<5)'}, {'variable': 'gc1_incident', 'vif': 1.05, 'multicollinearity_risk': 'Aceptable (<5)'}]`


## 4. Probabilidades Condicionales Causal DAG (pgmpy)

- P(Retraso L30 | Sin Incidente): `0.3036`
- P(Retraso L30 | Con Accidente GC-1): `0.7184`
- P(Riesgo Vuelo | Con Accidente GC-1): `0.4839`
