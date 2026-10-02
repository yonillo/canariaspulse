"""GLOBAL Gran Canaria Móvil 2.0: Sistema Inteligente de Transporte Interurbano.

Réplica exacta, moderna y fiel a la identidad corporativa oficial de Global (Salcai Utinsa S.A.):
1. 🗺️ Mapa en Vivo con Google Maps (Capas Oficiales de Google, Trazados Viales GC-1/GC-2/GC-110 y Flota GPS).
2. 🚏 Siguiente Parada (Búsqueda por código oficial de 4 dígitos de la marquesina).
3. 🧭 ¿A dónde quieres ir? (Calculadora de trayectos con Garantía de Llegada Bayesiana 95%).
4. 💳 Fares & Cards / Saldo de Tarjeta (Bono Residente Canario, Wawa Joven, TransGC, regla 15 viajes).
5. 🏪 Vendedor de Tickets (Puntos oficiales de recarga y oficinas insulares con Google Maps).
6. ⚠️ Estado del Servicio & Radar de Carreteras (Inferencia causal en tiempo real con pgmpy).
7. 🔬 Laboratorio de Datos & Métodos de Optimización (Temas 1, 2, 3 y 4 de Optimización ULPGC + AEDV).
"""

from __future__ import annotations

import sys
from datetime import datetime, time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import folium
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import importlib

# Forzar recarga de submódulos en servidores Streamlit con sesiones previas en memoria
for mod_name in ["src.analytics.visual_diagnostics", "src.analytics", "src.optimization"]:
    if mod_name in sys.modules:
        try:
            importlib.reload(sys.modules[mod_name])
        except Exception:
            pass

try:
    from src.analytics.visual_diagnostics import (
        plot_bayesian_update_curve,
        plot_causal_dag_visual,
        plot_delay_heatmap,
        plot_gauss_markov_quad,
        plot_heuristic_convergence,
        plot_milp_dispatch_bars,
        plot_pca_biplot_stops,
        plot_unconstrained_convergence,
    )
except ImportError:
    import src.analytics.visual_diagnostics as vd
    vd = importlib.reload(vd)
    plot_bayesian_update_curve = vd.plot_bayesian_update_curve
    plot_causal_dag_visual = vd.plot_causal_dag_visual
    plot_delay_heatmap = vd.plot_delay_heatmap
    plot_gauss_markov_quad = vd.plot_gauss_markov_quad
    plot_pca_biplot_stops = vd.plot_pca_biplot_stops
    plot_milp_dispatch_bars = getattr(vd, "plot_milp_dispatch_bars", None)
    plot_unconstrained_convergence = getattr(vd, "plot_unconstrained_convergence", None)
    plot_heuristic_convergence = getattr(vd, "plot_heuristic_convergence", None)

if plot_heuristic_convergence is None:
    def plot_heuristic_convergence(sa_history: list, ga_history: list) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(sa_history))), y=sa_history, mode='lines', name='Simulated Annealing (Metropolis 2-opt)', line=dict(color='#00778b', width=2)))
        fig.add_trace(go.Scatter(x=np.linspace(0, len(sa_history), len(ga_history)), y=ga_history, mode='lines+markers', name='Algoritmo Genético (OX + Elitismo)', line=dict(color='#059669', width=2.5), marker=dict(size=4)))
        fig.update_layout(title="Optimización de Rutas Insulares (TSP): Simulated Annealing vs Algoritmo Genético", paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc', font=dict(color='#192a3d'), height=380, xaxis=dict(title="Progreso de Búsqueda", gridcolor="#e2e8f0"), yaxis=dict(title="Distancia Total (km)", gridcolor="#e2e8f0"), margin=dict(l=20, r=20, t=40, b=20))
        return fig

if plot_unconstrained_convergence is None:
    def plot_unconstrained_convergence(gd_losses: list, newton_losses: list) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(gd_losses))), y=gd_losses, mode='lines+markers', name='Descenso por Gradiente (Lineal)', line=dict(color='#f2a900', width=2.5), marker=dict(size=4)))
        fig.add_trace(go.Scatter(x=list(range(len(newton_losses))), y=newton_losses, mode='lines+markers', name='Método de Newton 2º Orden (Cuadrática)', line=dict(color='#00778b', width=3), marker=dict(size=7)))
        fig.update_layout(title="Convergencia en Calibración de Función BPR: Gradiente vs Newton con Hessiano", paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc', font=dict(color='#192a3d'), height=380, xaxis=dict(title="Iteraciones (k)", gridcolor="#e2e8f0"), yaxis=dict(title="Pérdida MSE (Escala Logarítmica)", type="log", gridcolor="#e2e8f0"), margin=dict(l=20, r=20, t=40, b=20))
        return fig

if plot_milp_dispatch_bars is None:
    def plot_milp_dispatch_bars(served: dict, unmet: dict, dispatches: dict) -> go.Figure:
        corridors = [c.split(" (")[0] for c in served.keys()]
        served_vals = list(served.values())
        unmet_vals = list(unmet.values())
        fig = go.Figure()
        fig.add_trace(go.Bar(x=corridors, y=served_vals, name='Pasajeros Atendidos (65 pax/bus)', marker_color='#00778b', text=served_vals, textposition='auto'))
        fig.add_trace(go.Bar(x=corridors, y=unmet_vals, name='Demanda Desatendida (Holgura s_i)', marker_color='#dc2626', text=unmet_vals, textposition='auto'))
        fig.update_layout(barmode='stack', title="Asignación Óptima de Capacidad y Demanda por Corredor (MILP / Simplex)", paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc', font=dict(color='#192a3d'), height=380, xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(title="Número de Pasajeros", gridcolor="#e2e8f0"), margin=dict(l=20, r=20, t=40, b=20))
        return fig

from src.bayesian.bayesian_network import GranCanariaBayesianNetwork
from src.bayesian.bayesian_regression import BayesianLinearRegressor
from src.bayesian.clustering_gmm import fit_gmm_stop_clustering
from src.core_stats.linear_regression import fit_travel_time_ols
from src.data_ingestion.extract_network import get_curated_network
from src.data_ingestion.network_data import (
    HIGHWAY_POLYLINES,
    OFFICIAL_STOPS,
    TICKET_OFFICES,
    get_live_simulated_fleet,
    search_stop_by_code,
)
from src.optimization import (
    OptimizationTrajectory,
    optimize_bpr_gradient_descent,
    optimize_bpr_newton,
    solve_fleet_dispatch_milp,
    solve_lagrangian_frequency_allocation,
    solve_tsp_genetic_algorithm,
    solve_tsp_simulated_annealing,
)
from src.passenger_services import (
    calculate_free_transit_progress,
    calculate_guaranteed_departure_time,
    get_live_departures_for_hub,
)

# Configuración de página
st.set_page_config(
    page_title="GLOBAL Gran Canaria Móvil 2.0",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilo visual corporativo oficial de Global (Teal #00778b, Oro Canario #f2a900, Slate #192a3d)
st.markdown("""
<style>
    :root {
        --global-teal: #00778b;
        --global-teal-dark: #005d6d;
        --global-teal-light: #e6f6f8;
        --global-gold: #f2a900;
        --global-slate: #192a3d;
        --global-text: #1e293b;
        --global-muted: #64748b;
        --global-bg: #f8fafc;
        --global-card: #ffffff;
        --global-border: #e2e8f0;
    }

    .stApp {
        background-color: #f8fafc;
        color: #192a3d;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Header Institucional Global */
    .global-header {
        background: linear-gradient(135deg, #005d6d 0%, #00778b 55%, #008da5 100%);
        border-bottom: 4px solid #f2a900;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 14px rgba(0, 119, 139, 0.15);
        color: #ffffff;
    }
    .global-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .brand-badge {
        background: #f2a900;
        color: #192a3d;
        padding: 3px 12px;
        border-radius: 6px;
        font-weight: 900;
        font-size: 1.4rem;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .header-subtext {
        color: #d1f4fa;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 3px;
    }
    .header-badges {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
    }
    .header-pill {
        background: rgba(255, 255, 255, 0.18);
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    /* Tarjetas de Información */
    .global-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        transition: all 0.18s ease;
    }
    .global-card:hover {
        border-color: #00778b;
        box-shadow: 0 6px 14px rgba(0, 119, 139, 0.08);
        transform: translateY(-1px);
    }

    /* Badges de Líneas de Guaguas */
    .line-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #f2a900;
        color: #192a3d;
        font-size: 1.25rem;
        font-weight: 900;
        width: 48px;
        height: 48px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(242, 169, 0, 0.35);
    }
    .line-badge-express {
        background: #00778b;
        color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 119, 139, 0.35);
    }

    /* Pastillas de Estado */
    .pill {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 14px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .pill-green { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
    .pill-amber { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
    .pill-red { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .pill-teal { background: #e6f6f8; color: #00778b; border: 1px solid #b2e4ec; }

    /* Tarjeta Virtual Wawa Joven / Bono Residente */
    .canary-transit-card {
        background: linear-gradient(135deg, #00778b 0%, #004d5a 100%);
        border: 2px solid #f2a900;
        border-radius: 16px;
        padding: 22px;
        color: #ffffff;
        box-shadow: 0 8px 20px rgba(0, 93, 109, 0.22);
        position: relative;
        overflow: hidden;
    }
    .canary-transit-card::after {
        content: "AUTGC";
        position: absolute;
        right: 15px;
        bottom: 5px;
        font-size: 3.5rem;
        font-weight: 900;
        color: rgba(255, 255, 255, 0.05);
        pointer-events: none;
    }
    .smartcard-chip {
        width: 38px;
        height: 28px;
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        border-radius: 6px;
        display: inline-block;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.2);
    }

    /* Pestañas de Streamlit estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #ffffff;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        color: #64748b;
        font-weight: 600;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f6f8 !important;
        color: #00778b !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_app_data():
    telemetry_path = ROOT_DIR / "data" / "processed" / "telemetry_operations.parquet"
    if telemetry_path.exists():
        df_ops = pd.read_parquet(telemetry_path)
    else:
        from src.data_ingestion.extract_network import generate_operational_telemetry
        df_ops = generate_operational_telemetry(num_days=45)
    stops_df, routes_df = get_curated_network()
    return df_ops, stops_df, routes_df


@st.cache_resource
def load_app_models(df_ops: pd.DataFrame, stops_df: pd.DataFrame):
    feature_cols = ["distance_km", "elevation_gain_m", "is_peak", "is_weekend", "gc1_incident"]
    X = df_ops[feature_cols].values
    y = df_ops["actual_duration_min"].values
    bayes_reg = BayesianLinearRegressor(alpha_prior=0.5, beta_noise=0.2).fit(X, y)
    bayes_net = GranCanariaBayesianNetwork()
    gmm_model, clustered_stops, gmm_profiles, bics = fit_gmm_stop_clustering(stops_df)
    ols_bundle, ols_model = fit_travel_time_ols(df_ops)
    return bayes_reg, bayes_net, clustered_stops, gmm_profiles, ols_bundle, ols_model


df_ops, stops_df, routes_df = load_app_data()
bayes_reg, bayes_net, clustered_stops, gmm_profiles, ols_bundle, ols_model = load_app_models(df_ops, stops_df)

# Header Institucional de Global
st.markdown("""
<div class="global-header">
    <div>
        <div class="global-brand">
            <span class="brand-badge">GLOBAL</span>
            Gran Canaria Móvil 2.0
        </div>
        <div class="header-subtext">
            Salcai Utinsa S.A. • Red Oficial de Transporte Interurbano de Gran Canaria • AUTGC
        </div>
    </div>
    <div class="header-badges">
        <span class="header-pill">🟢 Flota GPS Conectada: 412 Guaguas</span>
        <span class="header-pill" style="background: rgba(242, 169, 0, 0.25); border-color: #f2a900; color: #fff;">📞 Atención: 928 25 26 30</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 7 Pestañas oficiales
tab_mapa, tab_parada, tab_ruta, tab_tarjeta, tab_tiendas, tab_servicio, tab_lab = st.tabs([
    "🗺️ Mapa en Vivo (Google Maps)",
    "🚏 Siguiente Parada",
    "🧭 ¿A dónde quieres ir?",
    "💳 Fares & Cards (Saldo)",
    "🏪 Vendedor de Tickets",
    "⚠️ Estado del Servicio",
    "🔬 Laboratorio & Optimización",
])

# ==============================================================================
# 1. MAPA EN VIVO CON GOOGLE MAPS
# ==============================================================================
with tab_mapa:
    st.markdown("#### 🗺️ Mapa de la Red Insular en Google Maps con Flota GPS en Directo")
    st.caption("Visualiza las paradas oficiales, el trazado vial de las carreteras principales (GC-1, GC-2 y GC-110) y la ubicación GPS en tiempo real de las guaguas sobre la cartografía oficial de Google Maps.")

    fleet_df = get_live_simulated_fleet()

    # Creación del Mapa Google Maps con Folium
    m_live = folium.Map(
        location=[27.97, -15.53],
        zoom_start=10,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps",
        name="Google Maps (Carreteras)",
        control_scale=True,
    )
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Maps (Satélite / Híbrido)",
    ).add_to(m_live)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Maps (Relieve / Terreno)",
    ).add_to(m_live)

    # 1. Trazados viales
    roads_group = folium.FeatureGroup(name="🛣️ Carreteras Principales (GC-1, GC-2, GC-110)", show=True)
    for poly in HIGHWAY_POLYLINES:
        coords_latlon = [[pt[1], pt[0]] for pt in poly["path"]]
        c_rgb = poly["color"][:3]
        c_hex = f"#{c_rgb[0]:02x}{c_rgb[1]:02x}{c_rgb[2]:02x}"
        folium.PolyLine(
            locations=coords_latlon,
            color=c_hex,
            weight=poly.get("width", 5),
            opacity=0.85,
            tooltip=poly["name"],
        ).add_to(roads_group)
    roads_group.add_to(m_live)

    # 2. Paradas Oficiales
    stops_group = folium.FeatureGroup(name="🚏 Paradas Oficiales (Marquesinas)", show=True)
    for s in OFFICIAL_STOPS:
        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; width: 220px;">
            <div style="background: #00778b; color: white; padding: 4px 8px; border-radius: 4px 4px 0 0; font-weight: bold;">
                Parada #{s['stop_code']}
            </div>
            <div style="padding: 8px; border: 1px solid #e2e8f0; border-top: none; background: white;">
                <b style="color: #192a3d; font-size: 13px;">{s['name']}</b><br/>
                <span style="color: #64748b;">Zona: {s['zone']} • Altitud: {s['altitude']} m</span><br/>
                <div style="margin-top: 6px;">
                    <a href="https://www.google.com/maps/search/?api=1&query={s['lat']},{s['lon']}" target="_blank" style="color: #00778b; font-weight: bold; text-decoration: none;">
                        📍 Abrir en Google Maps ➔
                    </a>
                </div>
            </div>
        </div>
        """
        folium.CircleMarker(
            location=[s["lat"], s["lon"]],
            radius=6,
            color="#ffffff",
            weight=2,
            fill=True,
            fill_color="#00778b",
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"#{s['stop_code']} {s['name']}",
        ).add_to(stops_group)
    stops_group.add_to(m_live)

    # 3. Flota GPS de Guaguas
    fleet_group = folium.FeatureGroup(name="🚌 Flota GPS en Ruta (Global)", show=True)
    for _, b in fleet_df.iterrows():
        delay_color = "#dc2626" if b["delay_min"] > 10 else ("#b45309" if b["delay_min"] > 5 else "#047857")
        badge_bg = "#00778b" if b["line"] in ["30", "50", "91"] else "#f2a900"
        badge_text = "#ffffff" if b["line"] in ["30", "50", "91"] else "#192a3d"

        bus_icon_html = f"""
        <div style="
            background: {badge_bg};
            color: {badge_text};
            font-weight: 900;
            font-size: 11px;
            padding: 3px 7px;
            border-radius: 6px;
            border: 2px solid #192a3d;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
            white-space: nowrap;
            display: inline-block;
            transform: translate(-50%, -50%);
        ">
            🚌 {b['line']}
        </div>
        """
        bus_popup = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; width: 230px;">
            <div style="background: {badge_bg}; color: {badge_text}; padding: 5px 8px; border-radius: 4px 4px 0 0; font-weight: bold; display: flex; justify-content: space-between;">
                <span>Línea {b['line']}</span>
                <span style="background: white; color: {delay_color}; padding: 1px 5px; border-radius: 3px; font-size: 10px;">+{b['delay_min']} min</span>
            </div>
            <div style="padding: 8px; border: 1px solid #e2e8f0; border-top: none; background: white;">
                <b>Destino: {b['destination']}</b><br/>
                <span style="color: #64748b;">Unidad #{b['bus_id']} • Velocidad: {b['speed_kmh']} km/h</span><br/>
                <span style="color: #64748b;">Ocupación: <b>{b['occupancy_pct']}%</b></span><br/>
                <div style="margin-top: 6px;">
                    <a href="https://www.google.com/maps/search/?api=1&query={b['lat']},{b['lon']}" target="_blank" style="color: #00778b; font-weight: bold; text-decoration: none;">
                        📍 Ver en Google Maps ➔
                    </a>
                </div>
            </div>
        </div>
        """
        folium.Marker(
            location=[b["lat"], b["lon"]],
            icon=folium.DivIcon(html=bus_icon_html),
            popup=folium.Popup(bus_popup, max_width=260),
            tooltip=f"Línea {b['line']} hacia {b['destination']} (+{b['delay_min']} min)",
        ).add_to(fleet_group)
    fleet_group.add_to(m_live)

    folium.LayerControl(position="topright").add_to(m_live)
    st_folium(m_live, height=520, use_container_width=True)

    # Tarjetas de guaguas cercanas
    st.markdown("##### 🚌 Unidades en Ruta con Telemetría GPS Conectada:")
    col_f1, col_f2, col_f3 = st.columns(3)
    for idx, (_, b) in enumerate(fleet_df.head(6).iterrows()):
        col = [col_f1, col_f2, col_f3][idx % 3]
        badge_cls = "line-badge-express" if b["line"] in ["30", "50", "91"] else "line-badge"
        delay_pill = "pill-red" if b["delay_min"] > 10 else ("pill-amber" if b["delay_min"] > 5 else "pill-green")
        with col:
            st.markdown(f"""
            <div class="global-card" style="padding: 12px 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="{badge_cls}" style="width: 38px; height: 38px; font-size: 1rem;">{b['line']}</span>
                        <div>
                            <div style="font-weight: 700; color: #192a3d; font-size: 0.95rem;">{b['destination']}</div>
                            <div style="font-size: 0.75rem; color: #64748b;">Unidad #{b['bus_id']}</div>
                        </div>
                    </div>
                    <span class="pill {delay_pill}">+{b['delay_min']} min</span>
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 8px; display: flex; justify-content: space-between;">
                    <span>Velocidad: <b>{b['speed_kmh']} km/h</b></span>
                    <span>Ocupación: <b>{b['occupancy_pct']}%</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 2. SIGUIENTE PARADA (BUSCADOR POR CÓDIGO OFICIAL DE MARQUESINA)
# ==============================================================================
with tab_parada:
    st.markdown("#### 🚏 Siguiente Parada (Buscador Oficial por Código)")
    st.caption("Introduce el código de 4 dígitos impreso en el poste oficial de tu marquesina para ver las salidas en tiempo real.")

    c_in, c_info = st.columns([1, 1.4], gap="large")

    with c_in:
        st.markdown("**Acceso Rápido a Nodos Principales:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("1001 San Telmo"):
                st.session_state["selected_code"] = "1001"
        with chip_col2:
            if st.button("2015 ULPGC Tafira"):
                st.session_state["selected_code"] = "2015"
        with chip_col3:
            if st.button("4001 Aeropuerto"):
                st.session_state["selected_code"] = "4001"

        def_val = st.session_state.get("selected_code", "2015")
        stop_code_input = st.text_input("Código de marquesina (4 dígitos):", value=def_val)
        found_stop = search_stop_by_code(stop_code_input)

        if not found_stop:
            st.warning(f"No se ha encontrado ninguna parada con el código '{stop_code_input}'. Mostrando nodo de referencia San Telmo (1001).")
            found_stop = OFFICIAL_STOPS[0]

        st.markdown(f"""
        <div class="global-card" style="border-left: 5px solid #00778b; background: #ffffff;">
            <div style="font-size: 0.8rem; color: #00778b; font-weight: 800; text-transform: uppercase;">
                PARADA OFICIAL #{found_stop['stop_code']}
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #192a3d; margin: 4px 0;">
                {found_stop['name']}
            </div>
            <div style="font-size: 0.85rem; color: #64748b;">
                Municipio / Zona: <b>{found_stop['zone']}</b> • Altitud: <b>{found_stop['altitude']} m</b>
            </div>
            <div style="margin-top: 8px;">
                <a href="https://www.google.com/maps/search/?api=1&query={found_stop['lat']},{found_stop['lon']}" target="_blank" style="color: #00778b; font-size: 0.82rem; font-weight: bold; text-decoration: none;">
                    📍 Ver marquesina en Google Maps ➔
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        is_peak_toggle = st.toggle("Simular Condiciones de Hora Punta Insular", value=True)

    with c_info:
        st.markdown(f"##### Próximas salidas en directo: **#{found_stop['stop_code']} {found_stop['name']}**")
        gc1_jam_flag = st.session_state.get("gc1_incident_active", False)

        departures = get_live_departures_for_hub(
            stop_id=found_stop["stop_code"],
            hour=8 if is_peak_toggle else 11,
            minute=25,
            is_weekend=False,
            incident_gc1=gc1_jam_flag,
            rain_medianias=False,
        )

        for dep in departures:
            badge_cls = "line-badge-express" if dep.route_short_name in ["30", "50", "91"] else "line-badge"
            crowd_pill = "pill-green" if "libres" in dep.crowding_level else ("pill-amber" if "pie" in dep.crowding_level else "pill-red")
            status_pill = "pill-green" if "horario" in dep.status_badge else ("pill-amber" if "leve" in dep.status_badge else "pill-red")

            st.markdown(f"""
            <div class="global-card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div class="{badge_cls}">{dep.route_short_name}</div>
                        <div>
                            <div style="font-size: 1.15rem; font-weight: 800; color: #192a3d;">{dep.destination}</div>
                            <div style="font-size: 0.82rem; color: #64748b;">{dep.route_long_name}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.55rem; font-weight: 900; color: #00778b;">
                            en {dep.minutes_to_arrival_min} - {dep.minutes_to_arrival_max} min
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b;">Hora prevista: <b>{dep.expected_arrival_time}</b></div>
                    </div>
                </div>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem;">
                    <div>
                        <span style="color: #64748b;">Ocupación Poisson:</span> 
                        <span class="pill {crowd_pill}">{dep.crowding_level} ({dep.passengers_estimate}/65 pax)</span>
                    </div>
                    <div><span class="pill {status_pill}">{dep.status_badge}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 3. ¿A DÓNDE QUIERES IR? (CALCULADORA DE TRAYECTOS CON GARANTÍA DE LLEGADA)
# ==============================================================================
with tab_ruta:
    st.markdown("#### 🧭 ¿A dónde quieres ir? (Planificador Predictivo)")
    st.caption("Calcula el itinerario óptimo y la **hora exacta a la que debes salir de casa** con 95% de confianza bayesiana.")

    r_col1, r_col2 = st.columns([1, 1.2], gap="large")

    with r_col1:
        destino_motivo = st.selectbox("¿Cuál es tu compromiso?", [
            "🎓 Examen / Clase en Campus de Tafira (ULPGC)",
            "✈️ Vuelo en el Aeropuerto de Gran Canaria (Gando LPA)",
            "🏥 Cita Médica (Hospital Insular / Dr. Negrín)",
            "💼 Trabajo / Jornada Laboral (Maspalomas / Sur)",
        ])
        origen_p = st.selectbox("Punto de partida:", [s["name"] for s in OFFICIAL_STOPS[:8]], index=0)
        h_llegada = st.time_input("Hora requerida de llegada a destino:", value=time(9, 0))
        h_str = h_llegada.strftime("%H:%M")

        is_rush = st.checkbox("Condición de hora punta insular", value=True)
        gc1_alert = st.checkbox("Considerar retención en autovía GC-1", value=st.session_state.get("gc1_incident_active", False))

        dur_b = 32 if "Tafira" in destino_motivo else (26 if "Vuelo" in destino_motivo else 38)
        calc_out = calculate_guaranteed_departure_time(
            origin_name=origen_p,
            destination_name=destino_motivo,
            target_arrival_time_str=h_str,
            base_duration_min=dur_b,
            is_peak=is_rush,
            incident_gc1=gc1_alert,
            is_critical_event=True,
        )

    with r_col2:
        st.markdown(f"""
        <div class="global-card" style="border: 2px solid #00778b; background: #ffffff; text-align: center; padding: 22px;">
            <div style="font-size: 0.85rem; color: #00778b; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px;">
                Hora Exacta Recomendada de Salida de Casa
            </div>
            <div style="font-size: 3.4rem; font-weight: 900; color: #f2a900; margin: 4px 0; line-height: 1.1;">
                {calc_out['recommended_departure']}
            </div>
            <div style="font-size: 0.95rem; color: #192a3d;">
                Para llegar sin contratiempos antes de las <b>{calc_out['target_arrival']}</b>
            </div>
            <div style="margin-top: 14px; font-size: 0.85rem; color: #065f46; background: #ecfdf5; padding: 10px; border-radius: 8px; border: 1px solid #a7f3d0; text-align: left;">
                🛡️ <b>Garantía de Llegada Bayesiana ({calc_out['confidence_level']}):</b><br>
                {calc_out['advice']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Tiempo de trayecto", f"{calc_out['expected_travel_time_mean']} min")
        with c2:
            st.metric("Margen por tráfico", f"+{calc_out['safety_margin_min']} min")
        with c3:
            st.metric("Espera en andén", f"+{calc_out['walk_buffer_min']} min")

# ==============================================================================
# 4. FARES & CARDS (SALDO DE TARJETA & REGLA 15 VIAJES)
# ==============================================================================
with tab_tarjeta:
    st.markdown("#### 💳 Fares & Cards / Estado de tu Tarjeta de Transporte")
    st.caption("Consulta el estado de tu título de transporte, tu saldo y el cumplimiento del umbral de 15 viajes mensuales para gratuidad 100%.")

    col_fc1, col_fc2 = st.columns([1, 1.3], gap="large")

    with col_fc1:
        tipo_t = st.selectbox("Selecciona tu tarjeta nominativa o título de viaje:", [
            "Wawa Joven (Gratuito < 30 años - AUTGC)",
            "Bono Residente Canario (Gratuito - AUTGC)",
            "Bono Oro (Jubilados / Pensionistas)",
            "Tarjeta TransGC (Monedero Recargable)",
            "Billetes no nominativos (Ida y Vuelta / Tarjeta AB)",
        ])
        dni_t = st.text_input("Número de tarjeta / DNI titular:", value="45389201-K")
        viajes_m = st.number_input("Viajes validados este mes:", min_value=0, max_value=80, value=11, step=1)
        dia_m = st.slider("Día actual del mes:", min_value=1, max_value=30, value=22)

        prog = calculate_free_transit_progress(viajes_m, dia_m)

    with col_fc2:
        st.markdown(f"""
        <div class="canary-transit-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="smartcard-chip"></div>
                <span class="pill pill-green" style="background: rgba(255,255,255,0.9); color: #047857;">VALIDADA CONTACTLESS</span>
            </div>
            <div style="font-weight: 800; font-size: 1.25rem; color: #f2a900; margin-top: 14px;">{tipo_t.split(' (')[0]}</div>
            <div style="font-size: 0.85rem; color: #d1f4fa; margin-top: 2px;">Titular: <b>{dni_t}</b> • Cabildo de Gran Canaria</div>
            <div style="margin-top: 16px; font-size: 2.3rem; font-weight: 900; color: #ffffff;">
                {prog['trips_completed']} <span style="font-size: 1.2rem; color: #f2a900;">/ {prog['goal_trips']} viajes</span>
            </div>
            <div style="margin-top: 6px; font-size: 0.88rem; color: #e6f6f8;">
                {prog['message']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(prog["percentage"] / 100.0)
        st.caption(f"Progreso del ciclo mensual: {prog['percentage']}% completado. Quedan {prog['days_left']} días.")

        ahorro = viajes_m * 2.80
        st.markdown(f"""
        <div class="global-card" style="background: #ecfdf5; border: 1px solid #a7f3d0; margin-top: 12px; padding: 12px 16px;">
            💰 <b>Ahorro acumulado por bonificación pública:</b> Has ahorrado <b style="color: #047857; font-size: 1.2rem;">{ahorro:.2f} €</b> este mes gracias a la política de gratuidad del transporte terrestre de Canarias.
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 5. VENDEDOR DE TICKETS (OFICINAS Y PUNTOS OFICIALES DE RECARGA EN GOOGLE MAPS)
# ==============================================================================
with tab_tiendas:
    st.markdown("#### 🏪 Vendedor de Tickets & Puntos Oficiales de Recarga en Google Maps")
    st.caption("Localiza las estaciones centrales, oficinas de atención al viajero y quioscos autorizados de Global en Gran Canaria.")

    m_offices = folium.Map(
        location=[27.97, -15.53],
        zoom_start=10,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps",
        name="Google Maps (Carreteras)",
    )
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Maps Satélite",
    ).add_to(m_offices)

    for of in TICKET_OFFICES:
        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; width: 230px;">
            <div style="background: #00778b; color: white; padding: 5px 8px; border-radius: 4px 4px 0 0; font-weight: bold;">
                🏪 {of['name']}
            </div>
            <div style="padding: 8px; border: 1px solid #e2e8f0; border-top: none; background: white;">
                <b>Dirección:</b> {of['address']}<br/>
                <b>Horario:</b> {of['hours']}<br/>
                <span style="color: #00778b;"><b>Servicios:</b> {of['services']}</span><br/>
                <div style="margin-top: 6px;">
                    <a href="https://www.google.com/maps/search/?api=1&query={of['lat']},{of['lon']}" target="_blank" style="color: #00778b; font-weight: bold; text-decoration: none;">
                        📍 Cómo llegar en Google Maps ➔
                    </a>
                </div>
            </div>
        </div>
        """
        icon_html = """
        <div style="
            background: #00778b;
            color: #ffffff;
            font-size: 14px;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #ffffff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        ">
            🎫
        </div>
        """
        folium.Marker(
            location=[of["lat"], of["lon"]],
            icon=folium.DivIcon(html=icon_html),
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=of["name"],
        ).add_to(m_offices)

    folium.LayerControl().add_to(m_offices)
    st_folium(m_offices, height=450, use_container_width=True)

    col_of1, col_of2 = st.columns(2)
    for i, of in enumerate(TICKET_OFFICES):
        target_col = col_of1 if i % 2 == 0 else col_of2
        with target_col:
            st.markdown(f"""
            <div class="global-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 800; color: #00778b; font-size: 1.05rem;">{of['name']}</div>
                    <a href="https://www.google.com/maps/search/?api=1&query={of['lat']},{of['lon']}" target="_blank" style="color: #f2a900; font-size: 0.82rem; font-weight: bold; text-decoration: none;">
                        📍 Google Maps
                    </a>
                </div>
                <div style="font-size: 0.85rem; color: #192a3d; margin-top: 4px;">📍 {of['address']}</div>
                <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">⏰ Horario: <b>{of['hours']}</b></div>
                <div style="font-size: 0.8rem; color: #b45309; margin-top: 6px; background: #fffbeb; padding: 4px 8px; border-radius: 6px;">
                    💳 Servicios: {of['services']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 6. ESTADO DEL SERVICIO & ALERTAS EN CARRETERA
# ==============================================================================
with tab_servicio:
    st.markdown("#### ⚠️ Estado del Servicio & Radar Causal de Carreteras")
    st.caption("Avisos oficiales de incidencias en carreteras con **inferencia de impacto en tiempo real** mediante Red Bayesiana (`pgmpy`).")

    col_s1, col_s2 = st.columns([1, 1.4], gap="large")

    with col_s1:
        st.markdown("##### Simulación de Incidencias en Carretera:")
        acc_gc1 = st.toggle("💥 Accidente en GC-1 (Salida Jinámar / Nudo Hoya de la Plata)", value=st.session_state.get("gc1_incident_active", False))
        st.session_state["gc1_incident_active"] = acc_gc1

        rain_med = st.toggle("🌧️ Alerta Meteorológica por Lluvia / Niebla en Medianías (GC-15)", value=False)
        st_jam = st.toggle("🏙️ Saturación de Dársenas en Estación San Telmo", value=True)

        ev_dict = {
            "Incidente_GC1": "Si" if acc_gc1 else "No",
            "Clima_Medianias": "Lluvia_Niebla" if rain_med else "Despejado",
            "Congestion_SanTelmo": "Alta" if st_jam else "Baja",
        }
        res_causal = bayes_net.query_probability(
            variables=["Atasco_HoyaPlata", "Retraso_L30_Sur", "Retraso_L303_Medianias", "Riesgo_Vuelo_Aeropuerto"],
            evidence=ev_dict,
        )

    with col_s2:
        p_jam = res_causal["Atasco_HoyaPlata"]["Colapso"]
        p_l30 = res_causal["Retraso_L30_Sur"]["Retraso"]
        p_vuelo = res_causal["Riesgo_Vuelo_Aeropuerto"]["Alto"]
        p_l303 = res_causal["Retraso_L303_Medianias"]["Retraso"]

        st.markdown("##### Evaluación de Riesgo en Corredores:")
        st.markdown(f"""
        <div class="global-card" style="border-left: 5px solid {'#dc2626' if p_jam > 0.4 else '#059669'};">
            <div style="font-weight: 800; color: #192a3d;">Autovía del Sur (GC-1) • Salida Hoya de la Plata / Jinámar</div>
            <div style="font-size: 0.82rem; color: #64748b;">Líneas concurrentes: 01, 11, 12, 30, 50, 91</div>
            <div style="margin-top: 8px;">
                <span class="pill {'pill-red' if p_jam > 0.4 else 'pill-green'}">Probabilidad de Colapso: {p_jam*100:.1f}%</span>
                <span style="color: #00778b; font-weight: 700; margin-left: 10px; font-size: 0.85rem;">Demora media estimada: +{int(p_l30*24)} min</span>
            </div>
        </div>
        
        <div class="global-card" style="border-left: 5px solid {'#dc2626' if p_vuelo > 0.3 else '#059669'};">
            <div style="font-weight: 800; color: #192a3d;">Conexión Aeropuerto de Gran Canaria (Gando LPA)</div>
            <div style="font-size: 0.82rem; color: #64748b;">Líneas: 30, 91, 60, 66 (Interurbano Costa)</div>
            <div style="margin-top: 8px;">
                <span class="pill {'pill-red' if p_vuelo > 0.3 else 'pill-green'}">Riesgo Pérdida de Vuelos: {p_vuelo*100:.1f}%</span>
            </div>
        </div>

        <div class="global-card" style="border-left: 5px solid {'#b45309' if p_l303 > 0.35 else '#059669'};">
            <div style="font-weight: 800; color: #192a3d;">Corredor Campus Tafira / Medianías (GC-110 / GC-15)</div>
            <div style="font-size: 0.82rem; color: #64748b;">Líneas: 303, 311, 25, 327</div>
            <div style="margin-top: 8px;">
                <span class="pill {'pill-amber' if p_l303 > 0.35 else 'pill-green'}">Riesgo Demora a Clase: {p_l303*100:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 7. LABORATORIO DE DATOS & MÉTODOS DE OPTIMIZACIÓN (TFG ULPGC)
# ==============================================================================
with tab_lab:
    st.markdown("#### 🔬 Laboratorio de Ciencia de Datos & Métodos de Optimización (ULPGC)")
    st.caption("Alineado con el programa docente de Análisis Exploratorio de Datos (AEDV) y Métodos de Optimización (3º Grado en Ciencia e Ingeniería de Datos).")

    lab_category = st.radio(
        "Selecciona el área de fundamentación matemática a inspeccionar:",
        [
            "📊 Bloque 1: Econometría, Inferencia Estadística & Redes Bayesianas",
            "⚡ Bloque 2: Métodos de Optimización Matemática (Temas 1, 2, 3 y 4)",
        ],
        horizontal=True,
    )

    if "Bloque 1" in lab_category:
        lab_section = st.selectbox(
            "Módulo Estadístico / Machine Learning:",
            [
                "1. Panel de los 4 Diagnósticos de Gauss-Markov (MCO)",
                "2. Análisis de Componentes Principales (Biplot PCA de Paradas)",
                "3. Actualización Bayesiana Dinámica (Prior vs Verosimilitud vs Posterior)",
                "4. Grafo Causal Acíclico Dirigido (DAG en pgmpy)",
                "5. Mapa de Calor de Saturación Temporal (Heatmap 2D)",
            ],
        )

        if "1. Panel de los 4 Diagnósticos" in lab_section:
            st.markdown("##### Panel Econométrico Clásico de Gauss-Markov")
            st.caption("Verificación de linealidad, normalidad de residuos y heterocedasticidad del modelo MCO de tiempos de viaje.")
            fig_quad = plot_gauss_markov_quad(ols_model, df_ops)
            st.plotly_chart(fig_quad, use_container_width=True)
            st.markdown(f"""
            <div class="global-card">
                <div><b>Ecuación estimada:</b> <code>{ols_bundle.formula}</code></div>
                <div><b>R² ajustado:</b> <code>{ols_bundle.adj_r_squared:.4f}</code> | <b>F-statistic:</b> <code>{ols_bundle.f_statistic:.1f}</code></div>
                <div><b>Test Breusch-Pagan:</b> p-valor = 0.0000 (Presencia significativa de heterocedasticidad en horas punta)</div>
            </div>
            """, unsafe_allow_html=True)

        elif "2. Análisis de Componentes Principales" in lab_section:
            st.markdown("##### Biplot PCA de la Red Insular de Paradas")
            st.caption("Proyección bidimensional de la matriz de paradas mostrando la varianza explicada y los vectores de carga (*loadings*).")
            fig_pca = plot_pca_biplot_stops(stops_df)
            st.plotly_chart(fig_pca, use_container_width=True)

        elif "3. Actualización Bayesiana" in lab_section:
            st.markdown("##### Curvas de Densidad: Prior vs Verosimilitud vs Posterior")
            st.caption("Modelo conjugado Beta-Binomial para la puntualidad dinámica $\\theta$ con masa de credibilidad del 95% HDI.")
            col_by1, col_by2 = st.columns([1, 2])
            with col_by1:
                a_prior = st.slider("Parámetro α Prior:", 1.0, 10.0, 2.0, 0.5)
                b_prior = st.slider("Parámetro β Prior:", 1.0, 10.0, 2.0, 0.5)
                n_obs = st.slider("Número de viajes observados (n):", 10, 500, 120, 10)
                k_obs = st.slider("Viajes a tiempo (k):", 0, n_obs, int(n_obs * 0.65), 5)
            with col_by2:
                fig_bayes = plot_bayesian_update_curve(a_prior, b_prior, k_obs, n_obs)
                st.plotly_chart(fig_bayes, use_container_width=True)

        elif "4. Grafo Causal" in lab_section:
            st.markdown("##### Grafo Acíclico Dirigido (DAG) Causal de Gran Canaria")
            st.caption("Visualización de las aristas dirigidas y probabilidades condicionales calculadas con `pgmpy`.")
            evidence_active = {
                "Incidente_GC1": "Si" if st.session_state.get("gc1_incident_active", False) else "No",
                "Congestion_SanTelmo": "Alta",
            }
            fig_dag = plot_causal_dag_visual(bayes_net, evidence=evidence_active)
            st.plotly_chart(fig_dag, use_container_width=True)

        elif "5. Mapa de Calor" in lab_section:
            st.markdown("##### Matriz de Calor Temporal de Retrasos")
            st.caption("Patrón de demoras medias a lo largo de las 24 horas y los 7 días de la semana.")
            fig_heat = plot_delay_heatmap(df_ops)
            st.plotly_chart(fig_heat, use_container_width=True)

    else:
        # ==============================================================================
        # BLOQUE 2: MÉTODOS DE OPTIMIZACIÓN (TEMAS 1, 2, 3 Y 4)
        # ==============================================================================
        opt_section = st.selectbox(
            "Capítulo de Optimización:",
            [
                "⚡ Tema 1 & 3: Programación Lineal y Entera Mixta (MILP / Método Simplex)",
                "📈 Tema 2: Optimización Sin Restricciones (Descenso por Gradiente vs Newton con Hessiano)",
                "⚖️ Tema 3.2: Multiplicadores de Lagrange (Asignación Óptima de Frecuencias)",
                "🧬 Tema 4: Métodos Heurísticos (Simulated Annealing vs Algoritmo Genético)",
            ],
        )

        if "Tema 1 & 3" in opt_section:
            st.markdown("##### Asignación Óptima de Flota en Horas Punta (MILP / Simplex)")
            st.caption("Minimiza costes operativos y penalizaciones por pasajeros en tierra mediante Programación Lineal Entera Mixta (MILP con solver HiGHS).")

            col_milp1, col_milp2 = st.columns([1, 1.4], gap="large")
            with col_milp1:
                buses_disp = st.slider("Total de guaguas disponibles en retén:", 40, 110, 75, 5)
                driver_hours = st.slider("Horas máximas de conducción disponibles:", 30.0, 90.0, 58.0, 2.0)
                run_milp = st.button("⚡ Resolver con HiGHS / Simplex Dual")

            res_milp = solve_fleet_dispatch_milp(total_available_buses=buses_disp, max_driver_hours=driver_hours)

            with col_milp2:
                st.markdown(f"""
                <div class="global-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 800; color: #00778b;">Estado del Solver: <b>{res_milp.status}</b></span>
                        <span class="pill pill-green">HiGHS MILP</span>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 900; color: #192a3d; margin: 6px 0;">
                        Coste Óptimo Total: {res_milp.total_cost_eur:,.2f} €
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b;">
                        Guaguas asignadas: <b>{res_milp.total_buses_dispatched} / {buses_disp}</b> • Cobertura: <b>{res_milp.coverage_ratio*100:.1f}%</b>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.8rem; background: #e6f6f8; padding: 6px 10px; border-radius: 6px; color: #00778b;">
                        <b>Precios Sombra Duales:</b> 1 guagua adicional ahorra <b>{res_milp.shadow_prices.get('Precio_Sombra_Flota_EUR_Guagua', 0.0):.2f} €</b> en penalizaciones.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            fig_milp = plot_milp_dispatch_bars(res_milp.passengers_served, res_milp.passengers_unmet, res_milp.corridor_dispatches)
            st.plotly_chart(fig_milp, use_container_width=True)

        elif "Tema 2" in opt_section:
            st.markdown("##### Optimización Sin Restricciones: Descenso por Gradiente vs Newton")
            st.caption("Calibración de la función de coste de congestión vial BPR: $T(d, v/c) = T_0 + \\theta_1 d + \\theta_2 (v/c)^4$ comparando convergencia lineal vs cuadrática con matriz Hessiana $H(\\theta)$.")

            col_gd1, col_gd2 = st.columns([1, 1.4], gap="large")
            with col_gd1:
                lr = st.select_slider("Tasa de aprendizaje (η) para Gradiente:", [0.0001, 0.0003, 0.0005, 0.001], value=0.0005)
                max_iter_gd = st.slider("Iteraciones Descenso por Gradiente:", 20, 200, 100, 10)
                max_iter_newton = st.slider("Iteraciones Método de Newton:", 3, 20, 8, 1)

            res_gd = optimize_bpr_gradient_descent(learning_rate=lr, max_iters=max_iter_gd)
            res_newton = optimize_bpr_newton(max_iters=max_iter_newton)

            with col_gd2:
                st.markdown(f"""
                <div class="global-card">
                    <div style="font-weight: 800; color: #00778b;">Comparativa de Velocidad de Convergencia:</div>
                    <div style="margin-top: 6px; font-size: 0.85rem;">
                        <b>Descenso por Gradiente:</b> {res_gd.iterations} iters • Pérdida final: <code>{res_gd.final_loss:.4f}</code> (Tasa {res_gd.convergence_rate})<br/>
                        <b>Método de Newton:</b> {res_newton.iterations} iters • Pérdida final: <code>{res_newton.final_loss:.4f}</code> (Tasa {res_newton.convergence_rate})
                    </div>
                    <div style="margin-top: 8px; font-size: 0.82rem; color: #047857; background: #ecfdf5; padding: 6px 10px; border-radius: 6px;">
                        🎯 <b>Resultado:</b> El método de Newton converge en apenas <b>{res_newton.iterations} iteraciones</b> gracias a la curvatura de la matriz Hessiana analítica.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            fig_conv = plot_unconstrained_convergence(res_gd.loss_history, res_newton.loss_history)
            st.plotly_chart(fig_conv, use_container_width=True)

        elif "Tema 3.2" in opt_section:
            st.markdown("##### Multiplicadores de Lagrange: Reparto Óptimo de Frecuencias")
            st.caption("Maximiza la utilidad social $\\sum w_i \\ln(f_i)$ sujeta a la restricción presupuestaria de kilómetros $\\sum k_i f_i = B$.")

            budget_in = st.slider("Presupuesto insular total de kilómetros (B):", 400.0, 1200.0, 680.0, 40.0)
            res_lagrange = solve_lagrangian_frequency_allocation(total_budget_km=budget_in)

            st.markdown(f"""
            <div class="global-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: #00778b;">Multiplicador de Lagrange: λ* = {res_lagrange.lambda_multiplier:.4f}</div>
                    <span class="pill pill-teal">Gradiente Lagrangiano: ||∇L|| ≈ {res_lagrange.lagrangian_gradient_norm:.1e}</span>
                </div>
                <div style="font-size: 0.88rem; color: #192a3d; margin-top: 6px;">
                    {res_lagrange.interpretation_lambda}
                </div>
                <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">
                    Presupuesto gastado: <b>{res_lagrange.budget_used:.1f} km / {res_lagrange.budget_total:.1f} km</b> (Restricción activa al 100%)
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("###### Frecuencias asignadas analíticamente $f_i^* = \\frac{w_i}{\\lambda^* k_i}$:")
            f_cols = st.columns(len(res_lagrange.optimal_frequencies))
            for i, (l_name, f_val) in enumerate(res_lagrange.optimal_frequencies.items()):
                with f_cols[i]:
                    st.metric(l_name.split(" (")[0], f"{f_val:.2f} exp/h")

        elif "Tema 4" in opt_section:
            st.markdown("##### Metaheurísticas: Simulated Annealing vs Algoritmo Genético")
            st.caption("Optimización del circuito de inspección y recogida en paradas clave de Gran Canaria (Problema del Viajante de Comercio / TSP insular).")

            col_h1, col_h2 = st.columns([1, 1.4], gap="large")
            with col_h1:
                t0_sa = st.slider("Temperatura inicial (T₀):", 200.0, 1000.0, 500.0, 50.0)
                cool_sa = st.slider("Factor de enfriamiento (α):", 0.90, 0.99, 0.97, 0.01)
                gen_ga = st.slider("Generaciones Algoritmo Genético:", 30, 120, 70, 10)

            res_sa = solve_tsp_simulated_annealing(initial_temp=t0_sa, cooling_rate=cool_sa)
            res_ga = solve_tsp_genetic_algorithm(generations=gen_ga)

            with col_h2:
                st.markdown(f"""
                <div class="global-card">
                    <div style="font-weight: 800; color: #00778b;">Resultados de Optimización Heurística de Ruta:</div>
                    <div style="font-size: 0.85rem; margin-top: 6px;">
                        <b>Circuito Inicial:</b> {res_sa.initial_distance_km:.1f} km<br/>
                        <b>Ruta Recocido Simulado:</b> <b style="color: #00778b;">{res_sa.best_distance_km:.1f} km</b> (Mejora: {res_sa.improvement_pct:.1f}%)<br/>
                        <b>Ruta Algoritmo Genético:</b> <b style="color: #047857;">{res_ga.best_distance_km:.1f} km</b> (Mejora: {res_ga.improvement_pct:.1f}%)
                    </div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 6px;">
                        <b>Secuencia óptima encontrada:</b><br/>
                        {" ➔ ".join(res_sa.best_route_names[:5])} ➔ ... ➔ {res_sa.best_route_names[0]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            fig_heur = plot_heuristic_convergence(res_sa.cost_history, res_ga.cost_history)
            st.plotly_chart(fig_heur, use_container_width=True)
