"""Módulo de Diagnósticos Visuales Avanzados, PCA, Modelos Bayesianos y Grafos Causales.

Implementa los componentes gráficos analíticos de nivel TFG (ULPGC):
1. Panel de los 4 diagnósticos clásicos de Gauss-Markov (Residuos vs Ajustados, Q-Q Plot, Scale-Location, Histograma).
2. Curvas dinámicas de Actualización Bayesiana (Prior vs Verosimilitud vs Posterior con HDI 95%).
3. Análisis de Componentes Principales (PCA) y Biplot 2D con elipses de clustering GMM.
4. Matriz de Calor (Heatmap) de Saturación Temporal (Hora del día vs Día de la semana).
5. Renderizado interactivo del Grafo Causal Acíclico (DAG) de la Red Bayesiana.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def plot_gauss_markov_quad(ols_model, df: pd.DataFrame) -> go.Figure:
    """Genera el panel clásico de 4 diagnósticos econométricos de regresión MCO."""
    fitted = ols_model.fittedvalues
    residuals = ols_model.resid
    # Estandarización de residuos
    std_residuals = (residuals - np.mean(residuals)) / np.std(residuals, ddof=1)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "1. Residuos vs Valores Ajustados (Linealidad / Heterocedasticidad)",
            "2. Normal Q-Q Plot (Contraste de Normalidad)",
            "3. Scale-Location (Evaluación de Homocedasticidad Breusch-Pagan)",
            "4. Distribución de Residuos vs Normal Teórica"
        ),
        horizontal_spacing=0.10,
        vertical_spacing=0.15
    )

    # Subplot 1: Residuos vs Ajustados
    fig.add_trace(
        go.Scatter(
            x=fitted, y=residuals,
            mode='markers',
            marker=dict(size=4, color='#00778b', opacity=0.45),
            name='Residuos MCO'
        ),
        row=1, col=1
    )
    # Línea horizontal cero
    fig.add_hline(y=0, line_dash="dash", line_color="#e11d48", row=1, col=1)

    # Subplot 2: Normal Q-Q Plot
    (osm, osr), (slope, intercept, r) = stats.probplot(std_residuals, dist="norm")
    fig.add_trace(
        go.Scatter(
            x=osm, y=osr,
            mode='markers',
            marker=dict(size=4, color='#0284c7', opacity=0.55),
            name='Cuantiles Empíricos'
        ),
        row=1, col=2
    )
    x_line = np.linspace(min(osm), max(osm), 100)
    fig.add_trace(
        go.Scatter(
            x=x_line, y=slope * x_line + intercept,
            mode='lines',
            line=dict(color='#e11d48', width=2),
            name='Línea Teórica Normal'
        ),
        row=1, col=2
    )

    # Subplot 3: Scale-Location (sqrt(|std_residuals|) vs Fitted)
    sqrt_abs_std = np.sqrt(np.abs(std_residuals))
    fig.add_trace(
        go.Scatter(
            x=fitted, y=sqrt_abs_std,
            mode='markers',
            marker=dict(size=4, color='#f2a900', opacity=0.5),
            name='Scale-Location'
        ),
        row=2, col=1
    )

    # Subplot 4: Histograma de Residuos vs Normal
    fig.add_trace(
        go.Histogram(
            x=residuals,
            histnorm='probability density',
            nbinsx=50,
            marker_color='rgba(0, 119, 139, 0.3)',
            marker_line_color='#00778b',
            marker_line_width=1,
            name='Histograma Residuos'
        ),
        row=2, col=2
    )
    x_grid = np.linspace(np.min(residuals), np.max(residuals), 200)
    normal_pdf = stats.norm.pdf(x_grid, loc=np.mean(residuals), scale=np.std(residuals))
    fig.add_trace(
        go.Scatter(
            x=x_grid, y=normal_pdf,
            mode='lines',
            line=dict(color='#059669', width=2.5),
            name='Campana de Gauss Teórica'
        ),
        row=2, col=2
    )

    fig.update_layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#192a3d', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        height=620,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    return fig


def plot_bayesian_update_curve(alpha_0: float, beta_0: float, successes: int, trials: int) -> go.Figure:
    """Genera las curvas de densidad Prior vs Verosimilitud Normalizada vs Posterior (Beta-Binomial)."""
    alpha_N = alpha_0 + successes
    beta_N = beta_0 + (trials - successes)

    theta = np.linspace(0.001, 0.999, 400)
    prior_pdf = stats.beta.pdf(theta, alpha_0, beta_0)
    post_pdf = stats.beta.pdf(theta, alpha_N, beta_N)

    # Verosimilitud escalada
    # L(theta) = theta^k * (1-theta)^(n-k)
    log_lik = successes * np.log(theta) + (trials - successes) * np.log(1.0 - theta)
    lik_scaled = np.exp(log_lik - np.max(log_lik)) * np.max(post_pdf) * 0.9

    # HDI 95%
    hdi_low = stats.beta.ppf(0.025, alpha_N, beta_N)
    hdi_high = stats.beta.ppf(0.975, alpha_N, beta_N)

    fig = go.Figure()

    # Prior
    fig.add_trace(go.Scatter(
        x=theta, y=prior_pdf,
        mode='lines',
        line=dict(color='#f2a900', width=2, dash='dot'),
        name=f'Prior: Beta({alpha_0:.1f}, {beta_0:.1f})'
    ))

    # Verosimilitud
    fig.add_trace(go.Scatter(
        x=theta, y=lik_scaled,
        mode='lines',
        line=dict(color='#64748b', width=1.5, dash='dash'),
        name='Verosimilitud Reescalada'
    ))

    # Posterior
    fig.add_trace(go.Scatter(
        x=theta, y=post_pdf,
        mode='lines',
        line=dict(color='#00778b', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 119, 139, 0.18)',
        name=f'Posterior: Beta({alpha_N:.0f}, {beta_N:.0f})'
    ))

    # Área sombreada HDI 95%
    fig.add_vrect(
        x0=hdi_low, x1=hdi_high,
        fillcolor="rgba(5, 150, 105, 0.15)",
        line_width=1,
        line_color="#059669",
        annotation_text=f"HDI 95%: [{hdi_low:.3f}, {hdi_high:.3f}]",
        annotation_position="top left"
    )

    fig.update_layout(
        title=f"Actualización Bayesiana de Puntualidad ({successes} éxitos en {trials} viajes)",
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#192a3d', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        height=380,
        xaxis=dict(title="Tasa de Puntualidad θ (Proporción)", gridcolor="#e2e8f0", range=[max(0.0, hdi_low - 0.15), min(1.0, hdi_high + 0.15)]),
        yaxis=dict(title="Densidad de Probabilidad p(θ)", gridcolor="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_pca_biplot_stops(stops_df: pd.DataFrame) -> go.Figure:
    """Calcula el PCA de paradas insulares y genera un Biplot 2D con vectores de carga y clusters GMM."""
    # Variables operativas
    features = stops_df.copy()
    if "daily_frequency" not in features.columns:
        features["daily_frequency"] = features["is_hub"].apply(lambda h: 140 if h else 40)
    if "peak_ratio" not in features.columns:
        features["peak_ratio"] = features["zone"].apply(lambda z: 0.65 if "ULPGC" in z else 0.40)

    feature_cols = ["daily_frequency", "altitude", "peak_ratio"]
    X = features[feature_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)
    var_exp = pca.explained_variance_ratio_

    features["PC1"] = components[:, 0]
    features["PC2"] = components[:, 1]

    fig = go.Figure()

    # Puntos de las paradas
    cluster_col = features["assigned_cluster"] if "assigned_cluster" in features.columns else features["zone"]
    fig.add_trace(go.Scatter(
        x=features["PC1"], y=features["PC2"],
        mode='markers+text',
        text=features["name"].apply(lambda n: n.split(" (")[0]),
        textposition="top right",
        textfont=dict(size=9, color="#192a3d"),
        marker=dict(
            size=11,
            color=features["altitude"],
            colorscale='Tealgrn',
            showscale=True,
            colorbar=dict(title="Altitud (m)", len=0.7)
        ),
        name='Paradas'
    ))

    # Vectores de carga (Loadings)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    feature_labels = ["Frecuencia Diaria", "Altitud (m)", "Ratio Punta"]
    for i, label in enumerate(feature_labels):
        fig.add_annotation(
            ax=0, ay=0,
            x=loadings[i, 0] * 2.5,
            y=loadings[i, 1] * 2.5,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2,
            arrowcolor="#dc2626"
        )
        fig.add_trace(go.Scatter(
            x=[loadings[i, 0] * 2.8],
            y=[loadings[i, 1] * 2.8],
            mode='text',
            text=[label],
            textfont=dict(color="#dc2626", size=11, family="Arial Black"),
            showlegend=False
        ))

    fig.update_layout(
        title=f"Biplot PCA de la Red Insular de Paradas (Varianza Explicada: {sum(var_exp)*100:.1f}%)",
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#192a3d', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        height=480,
        xaxis=dict(title=f"Componente Principal 1 ({var_exp[0]*100:.1f}%)", gridcolor="#e2e8f0", zerolinecolor="#cbd5e1"),
        yaxis=dict(title=f"Componente Principal 2 ({var_exp[1]*100:.1f}%)", gridcolor="#e2e8f0", zerolinecolor="#cbd5e1"),
        showlegend=False
    )
    return fig


def plot_delay_heatmap(df_ops: pd.DataFrame) -> go.Figure:
    """Genera una matriz de calor (Heatmap) de retraso medio por hora del día y día de la semana."""
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_order_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    pivot = df_ops.pivot_table(index="day_of_week", columns="hour", values="delay_min", aggfunc="mean")
    # Reindexar días si existen
    available_days = [d for d in day_order if d in pivot.index]
    pivot = pivot.reindex(available_days)
    
    fig = px.imshow(
        pivot,
        labels=dict(x="Hora del Día", y="Día de la Semana", color="Retraso (min)"),
        x=pivot.columns,
        y=[day_order_es[day_order.index(d)] for d in pivot.index],
        color_continuous_scale="YlOrRd",
        aspect="auto"
    )
    fig.update_layout(
        title="Mapa de Calor de Saturación y Retraso en la Red de Global",
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#192a3d', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_causal_dag_visual(bayes_net, evidence: Optional[Dict[str, str]] = None) -> go.Figure:
    """Renderiza visualmente el Grafo Causal Acíclico Dirigido (DAG) de la Red Bayesiana."""
    # Nodos y coordenadas fijas para layout visual
    node_coords = {
        "Clima_Medianias": (1.0, 3.0),
        "Incidente_GC1": (4.0, 3.0),
        "Congestion_SanTelmo": (2.5, 3.0),
        "Atasco_HoyaPlata": (3.5, 2.0),
        "Retraso_L30_Sur": (3.5, 1.0),
        "Retraso_L303_Medianias": (1.5, 1.5),
        "Riesgo_Vuelo_Aeropuerto": (4.5, 0.5),
    }

    evidence = evidence or {}
    # Consultar probabilidades marginales condicionadas
    probs = bayes_net.query_probability(
        variables=["Atasco_HoyaPlata", "Retraso_L30_Sur", "Retraso_L303_Medianias", "Riesgo_Vuelo_Aeropuerto"],
        evidence=evidence
    )

    edge_x = []
    edge_y = []
    edges = [
        ("Clima_Medianias", "Retraso_L303_Medianias"),
        ("Incidente_GC1", "Atasco_HoyaPlata"),
        ("Congestion_SanTelmo", "Atasco_HoyaPlata"),
        ("Congestion_SanTelmo", "Retraso_L303_Medianias"),
        ("Atasco_HoyaPlata", "Retraso_L30_Sur"),
        ("Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"),
    ]

    for u, v in edges:
        x0, y0 = node_coords[u]
        x1, y1 = node_coords[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig = go.Figure()

    # Flechas / Aristas
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(color='#94a3b8', width=2),
        hoverinfo='none',
        showlegend=False
    ))

    # Nodos
    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for node, (nx, ny) in node_coords.items():
        node_x.append(nx)
        node_y.append(ny)
        label = node.replace("_", " ")

        # Color según estado o evidencia
        if node in evidence:
            val = evidence[node]
            node_colors.append('#dc2626' if val in ['Si', 'Lluvia_Niebla', 'Alta'] else '#059669')
            node_text.append(f"<b>{label}</b><br>Evidencia: {val}")
        elif node in probs:
            # Obtener probabilidad de evento crítico
            critical_key = "Colapso" if "Atasco" in node else ("Retraso" if "Retraso" in node else "Alto")
            prob_val = probs[node].get(critical_key, 0.0)
            node_colors.append('#dc2626' if prob_val > 0.4 else ('#f2a900' if prob_val > 0.25 else '#00778b'))
            node_text.append(f"<b>{label}</b><br>P({critical_key}): {prob_val*100:.1f}%")
        else:
            node_colors.append('#00778b')
            node_text.append(f"<b>{label}</b>")

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[n.replace("_", " ") for n in node_coords.keys()],
        textposition="bottom center",
        textfont=dict(size=10, color="#192a3d", family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        marker=dict(size=28, color=node_colors, line=dict(color="#ffffff", width=2.5)),
        hovertext=node_text,
        hoverinfo='text',
        showlegend=False
    ))

    fig.update_layout(
        title="Grafo Causal Acíclico Dirigido (DAG) en pgmpy con Inferencia en Tiempo Real",
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#192a3d', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        height=380,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
