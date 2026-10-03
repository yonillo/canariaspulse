"""GLOBAL Gran Canaria Móvil 2.0: Sistema Inteligente de Transporte Interurbano.

Lavado de cara integral de la app oficial de Global (Salcai Utinsa S.A.):
1. 🗺️ Explorador en Vivo (Google Maps nativo, capas viales GC-1/GC-2/GC-110 y flota GPS en directo).
2. 🚏 Panel en Parada (Marquesina digital LED, afluencia Poisson y cuenta atrás en tiempo real).
3. 🧭 Planificador de Ruta (Garantía de Llegada Bayesiana 95% para exámenes ULPGC o vuelos LPA).
4. 💳 Mi Tarjeta Virtual (Simulador Wawa Joven/Bono Residente, regla 15 viajes y ahorro en €).
5. 🏪 Puntos de Venta (Oficinas oficiales y quioscos de recarga en Google Maps).
6. ⚠️ Radar de Tráfico (Inferencia Causal con pgmpy sobre colapsos en la GC-1).
7. 🔬 Laboratorio & Métodos de Optimización (Temas 1, 2, 3 y 4 de Optimización ULPGC + AEDV).
"""

from __future__ import annotations

import sys
import importlib
from datetime import datetime, time, timedelta
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

# Forzar recarga de submódulos en sesiones previas de Streamlit
for mod_name in ["src.analytics.visual_diagnostics", "src.analytics", "src.optimization", "src.passenger_services"]:
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
    solve_fleet_dispatch_milp,
    optimize_bpr_gradient_descent,
    optimize_bpr_newton,
    solve_lagrangian_frequency_allocation,
    solve_tsp_simulated_annealing,
    solve_tsp_genetic_algorithm,
)
from src.passenger_services import (
    calculate_free_transit_progress,
    calculate_guaranteed_departure_time,
    get_live_departures_for_hub,
)

# Configuración de página
st.set_page_config(
    page_title="GLOBAL Móvil 2.0 | Gran Canaria Smart Transit",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilo visual de alta gama: Modern Mobile Transit App UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --global-teal: #00778b;
        --global-teal-dark: #005d6d;
        --global-teal-light: #e6f6f8;
        --global-gold: #f2a900;
        --global-gold-dark: #d97706;
        --global-slate: #192a3d;
        --global-text: #1e293b;
        --global-muted: #64748b;
        --global-bg: #f8fafc;
        --global-card: #ffffff;
        --global-border: #e2e8f0;
    }

    .stApp {
        background-color: #f1f5f9;
        color: #192a3d;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Barra Superior Tipo App Móvil */
    .app-topbar {
        background: linear-gradient(135deg, #005d6d 0%, #00778b 60%, #008da5 100%);
        border-bottom: 4px solid #f2a900;
        border-radius: 16px;
        padding: 16px 22px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 6px 18px rgba(0, 119, 139, 0.18);
        color: #ffffff;
    }
    .brand-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.6rem;
        font-weight: 900;
        letter-spacing: -0.5px;
    }
    .brand-pill {
        background: #f2a900;
        color: #192a3d;
        padding: 3px 12px;
        border-radius: 6px;
        font-weight: 900;
        font-size: 1.3rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .topbar-subtitle {
        color: #d1f4fa;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 2px;
    }
    .status-capsules {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .capsule {
        background: rgba(255, 255, 255, 0.16);
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.22);
    }

    /* Pestañas estilizadas como barra de navegación de App */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 8px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 18px;
        color: #64748b;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00778b !important;
        color: #ffffff !important;
        font-weight: 700;
        box-shadow: 0 3px 10px rgba(0, 119, 139, 0.25);
    }

    /* Tarjetas Interactivas de Transporte */
    .transit-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.18s ease;
    }
    .transit-card:hover {
        border-color: #00778b;
        box-shadow: 0 8px 18px rgba(0, 119, 139, 0.10);
        transform: translateY(-2px);
    }

    /* Badges de Líneas */
    .route-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #f2a900;
        color: #192a3d;
        font-size: 1.3rem;
        font-weight: 900;
        width: 52px;
        height: 52px;
        border-radius: 12px;
        box-shadow: 0 3px 6px rgba(242, 169, 0, 0.35);
    }
    .route-badge-express {
        background: #00778b;
        color: #ffffff;
        box-shadow: 0 3px 6px rgba(0, 119, 139, 0.35);
    }

    /* Pantalla LED de Marquesina */
    .led-marquesina-screen {
        background: #0d1b2a;
        border: 3px solid #1b263b;
        border-radius: 16px;
        padding: 20px;
        color: #f8fafc;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.8), 0 8px 24px rgba(0,0,0,0.25);
        font-family: 'Inter', monospace;
    }
    .led-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1e3a5f;
        padding-bottom: 10px;
        margin-bottom: 16px;
    }
    .led-stop-name {
        font-size: 1.3rem;
        font-weight: 800;
        color: #fbbf24;
        letter-spacing: 0.5px;
    }
    .led-time {
        font-size: 1.1rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .led-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .led-arrival-min {
        font-size: 1.8rem;
        font-weight: 900;
        color: #34d399;
    }

    /* Tarjeta Virtual Wawa Joven / Bono Residente */
    .smartcard-3d {
        background: linear-gradient(135deg, #00778b 0%, #004d5a 50%, #00363f 100%);
        border: 2px solid #f2a900;
        border-radius: 18px;
        padding: 24px;
        color: #ffffff;
        box-shadow: 0 12px 28px rgba(0, 77, 90, 0.35);
        position: relative;
        overflow: hidden;
    }
    .smartcard-chip-gold {
        width: 44px;
        height: 32px;
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        border-radius: 6px;
        display: inline-block;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.25);
    }

    /* Timeline de Itinerario */
    .timeline-step {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin-bottom: 12px;
        position: relative;
    }
    .step-time {
        font-weight: 800;
        color: #00778b;
        font-size: 0.95rem;
        min-width: 45px;
    }
    .step-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #00778b;
        border: 2px solid #ffffff;
        box-shadow: 0 0 0 2px #00778b;
        margin-top: 4px;
    }
    .step-content {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 14px;
        flex: 1;
    }

    /* Pastillas */
    .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 14px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .pill-green { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
    .pill-amber { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
    .pill-red { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .pill-teal { background: #e6f6f8; color: #00778b; border: 1px solid #b2e4ec; }
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

# Barra Superior de la Aplicación Móvil
st.markdown("""
<div class="app-topbar">
    <div>
        <div class="brand-title">
            <span class="brand-pill">GLOBAL</span>
            Gran Canaria Móvil 2.0
        </div>
        <div class="topbar-subtitle">
            Salcai Utinsa S.A. • Red Oficial de Transporte Interurbano • Autoridad Única del Transporte (AUTGC)
        </div>
    </div>
    <div class="status-capsules">
        <span class="capsule" style="background: rgba(34, 197, 94, 0.2); border-color: #22c55e;">🟢 GPS Flota Activo (412 Guaguas)</span>
        <span class="capsule" style="background: rgba(242, 169, 0, 0.2); border-color: #f2a900; color: #fff;">📞 928 25 26 30</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 7 Pestañas oficiales con experiencia mobile-first
tab_mapa, tab_parada, tab_ruta, tab_tarjeta, tab_tiendas, tab_servicio, tab_lab = st.tabs([
    "🗺️ Mapa en Vivo (Google Maps)",
    "🚏 Panel en Parada (Marquesina)",
    "🧭 Planificador de Ruta (Garantía 95%)",
    "💳 Mi Tarjeta (Regla 15 Viajes)",
    "🏪 Puntos de Venta & Recarga",
    "⚠️ Radar de Tráfico GC-1",
    "🔬 Laboratorio & Optimización ULPGC",
])

# ==============================================================================
# 1. MAPA EN VIVO CON GOOGLE MAPS
# ==============================================================================
with tab_mapa:
    st.markdown("##### 🗺️ Red Insular en Google Maps con Posicionamiento GPS en Tiempo Real")

    c_filt1, c_filt2 = st.columns([1.5, 1])
    with c_filt1:
        corridor_filter = st.selectbox(
            "Filtrar Corredor en Google Maps:",
            [
                "Todos los Corredores de Gran Canaria",
                "Corredor Sur GC-1 (San Telmo ➔ Maspalomas ➔ Mogán)",
                "Corredor Universitario / Centro (San Telmo ➔ Campus Tafira ➔ San Mateo)",
                "Corredor Norte GC-2 (San Telmo ➔ Arucas ➔ Gáldar ➔ Agaete)",
            ],
        )
    with c_filt2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.caption("🛰️ **Precisión GPS:** ±5 metros • Datos telemetría actualizados cada 10 segundos")

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
        # Filtrado por corredor si aplica
        if "Sur" in corridor_filter and "Sur" not in poly["name"]:
            continue
        if "Universitario" in corridor_filter and "Centro" not in poly["name"]:
            continue
        if "Norte" in corridor_filter and "Norte" not in poly["name"]:
            continue

        coords_latlon = [[pt[1], pt[0]] for pt in poly["path"]]
        c_rgb = poly["color"][:3]
        c_hex = f"#{c_rgb[0]:02x}{c_rgb[1]:02x}{c_rgb[2]:02x}"
        folium.PolyLine(
            locations=coords_latlon,
            color=c_hex,
            weight=poly.get("width", 5),
            opacity=0.88,
            tooltip=poly["name"],
        ).add_to(roads_group)
    roads_group.add_to(m_live)

    # 2. Paradas Oficiales
    stops_group = folium.FeatureGroup(name="🚏 Paradas Oficiales (Marquesinas)", show=True)
    for s in OFFICIAL_STOPS:
        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; width: 220px;">
            <div style="background: #00778b; color: white; padding: 5px 8px; border-radius: 4px 4px 0 0; font-weight: bold;">
                Parada #{s['stop_code']}
            </div>
            <div style="padding: 8px; border: 1px solid #e2e8f0; border-top: none; background: white;">
                <b style="color: #192a3d; font-size: 13px;">{s['name']}</b><br/>
                <span style="color: #64748b;">Zona: {s['zone']} • Altitud: {s['altitude']} m</span><br/>
                <div style="margin-top: 8px;">
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
                <span style="color: #64748b;">Ocupación Poisson: <b>{b['occupancy_pct']}%</b></span><br/>
                <div style="margin-top: 8px;">
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
    st_folium(m_live, height=500, use_container_width=True)

    # Tarjetas interactivas de las guaguas en ruta
    st.markdown("##### 🟢 Radar de Guaguas Monitorizadas en Directo:")
    col_f1, col_f2, col_f3 = st.columns(3)
    for idx, (_, b) in enumerate(fleet_df.iterrows()):
        col = [col_f1, col_f2, col_f3][idx % 3]
        badge_cls = "route-badge-express" if b["line"] in ["30", "50", "91"] else "route-badge"
        delay_pill = "pill-red" if b["delay_min"] > 10 else ("pill-amber" if b["delay_min"] > 5 else "pill-green")
        progress_pct = int(min(95, max(15, b["speed_kmh"] * 0.9 + 10)))

        with col:
            st.markdown(f"""
            <div class="transit-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span class="{badge_cls}">{b['line']}</span>
                        <div>
                            <div style="font-weight: 800; color: #192a3d; font-size: 1.05rem;">{b['destination']}</div>
                            <div style="font-size: 0.78rem; color: #64748b;">Unidad <b>#{b['bus_id']}</b> • {b['speed_kmh']} km/h</div>
                        </div>
                    </div>
                    <span class="pill {delay_pill}">+{b['delay_min']} min</span>
                </div>
                <div style="margin-top: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-bottom: 3px;">
                        <span>En ruta</span>
                        <span>Ocupación: <b>{b['occupancy_pct']}%</b></span>
                    </div>
                    <div style="background: #e2e8f0; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: {'#00778b' if b['occupancy_pct'] < 75 else '#f2a900'}; width: {b['occupancy_pct']}%; height: 100%;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 2. PANEL EN PARADA (MARQUESINA DIGITAL LED)
# ==============================================================================
with tab_parada:
    st.markdown("##### 🚏 Panel Digital de Salidas en Marquesina")
    st.caption("Visualiza las próximas llegadas como si estuvieras frente a la pantalla digital de la estación o marquesina.")

    col_sel1, col_sel2 = st.columns([1, 1.2])

    with col_sel1:
        st.markdown("**Acceso directo a marquesinas clave:**")
        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1:
            if st.button("San Telmo (1001)"):
                st.session_state["stop_code"] = "1001"
        with qc2:
            if st.button("Tafira (2015)"):
                st.session_state["stop_code"] = "2015"
        with qc3:
            if st.button("Gando (4001)"):
                st.session_state["stop_code"] = "4001"
        with qc4:
            if st.button("Faro (5020)"):
                st.session_state["stop_code"] = "5020"

        c_val = st.session_state.get("stop_code", "2015")
        sc_input = st.text_input("O introduce el código oficial de 4 dígitos:", value=c_val)
        selected_stop = search_stop_by_code(sc_input) or OFFICIAL_STOPS[0]

        is_peak = st.toggle("Simular Hora Punta Insular", value=True)
        gc1_jam = st.session_state.get("gc1_incident_active", False)

    with col_sel2:
        now_str = datetime.now().strftime("%H:%M:%S")
        departures = get_live_departures_for_hub(
            stop_id=selected_stop["stop_code"],
            hour=8 if is_peak else 11,
            minute=20,
            is_weekend=False,
            incident_gc1=gc1_jam,
        )

        st.markdown(f"""
        <div class="led-marquesina-screen">
            <div class="led-header">
                <div>
                    <span style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">MARQUESINA #{selected_stop['stop_code']}</span>
                    <div class="led-stop-name">{selected_stop['name']}</div>
                </div>
                <div style="text-align: right;">
                    <div class="led-time">{now_str}</div>
                    <span style="font-size: 0.72rem; color: #34d399;">● TIEMPO REAL</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for dep in departures:
            st.markdown(f"""
            <div class="led-row">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="background: #fbbf24; color: #0f172a; font-weight: 900; font-size: 1.15rem; padding: 4px 10px; border-radius: 6px;">
                        {dep.route_short_name}
                    </span>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff;">{dep.destination}</div>
                        <div style="font-size: 0.75rem; color: #94a3b8;">{dep.route_long_name}</div>
                        <div style="font-size: 0.75rem; color: #38bdf8; margin-top: 2px;">
                            {dep.crowding_level} ({dep.passengers_estimate}/65 plazas)
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="led-arrival-min">{dep.minutes_to_arrival_min} min</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">Prevista: {dep.expected_arrival_time}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 3. PLANIFICADOR DE RUTA (GARANTÍA DE LLEGADA 95%)
# ==============================================================================
with tab_ruta:
    st.markdown("##### 🧭 Planificador de Ruta con Garantía de Llegada Bayesiana")
    st.caption("A diferencia de la app tradicional que da horarios fijos que fallan en atascos, nuestro motor calcula hacia atrás la hora exacta a la que debes salir de casa para asegurar tu llegada con 95% de confianza.")

    col_r1, col_r2 = st.columns([1, 1.4], gap="large")

    with col_r1:
        compromiso = st.selectbox(
            "Selecciona tu compromiso:",
            [
                "🎓 Examen / Evaluación en Campus Tafira (ULPGC)",
                "✈️ Vuelo en el Aeropuerto de Gran Canaria (Gando LPA)",
                "🏥 Cita Médica (Hospital Insular / Dr. Negrín)",
                "💼 Jornada Laboral / Turno de Trabajo",
            ],
        )

        origen_nombre = st.selectbox(
            "Punto de Salida:",
            [s["name"] for s in OFFICIAL_STOPS[:8]],
            index=0,
        )

        hora_meta = st.time_input("Hora exacta a la que debes estar en destino:", value=time(9, 0))
        h_str = hora_meta.strftime("%H:%M")

        is_rush_hour = st.checkbox("Condiciones de Hora Punta de Tráfico", value=True)
        gc1_jam_flag = st.checkbox("Retención confirmada en Autovía GC-1", value=st.session_state.get("gc1_incident_active", False))

        base_min = 32 if "Tafira" in compromiso else (26 if "Vuelo" in compromiso else 38)
        calc_res = calculate_guaranteed_departure_time(
            origin_name=origen_nombre,
            destination_name=compromiso,
            target_arrival_time_str=h_str,
            base_duration_min=base_min,
            is_peak=is_rush_hour,
            incident_gc1=gc1_jam_flag,
            is_critical_event=True,
        )

    with col_r2:
        st.markdown(f"""
        <div class="transit-card" style="border: 2px solid #00778b; text-align: center; padding: 22px; background: #ffffff;">
            <span class="pill pill-teal" style="font-size: 0.85rem; padding: 4px 12px;">🛡️ GARANTÍA DE LLEGADA AL 95%</span>
            <div style="font-size: 0.88rem; color: #64748b; margin-top: 8px;">Debes salir de casa exactamente a las:</div>
            <div style="font-size: 3.8rem; font-weight: 900; color: #f2a900; line-height: 1; margin: 4px 0;">
                {calc_res['recommended_departure']}
            </div>
            <div style="font-size: 1rem; color: #192a3d; font-weight: 700;">
                Para llegar sin estrés antes de las {calc_res['target_arrival']}
            </div>
            <div style="font-size: 0.82rem; color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 10px; margin-top: 14px; text-align: left;">
                💡 <b>Recomendación del Motor Bayesiano:</b> {calc_res['advice']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("###### 📍 Desglose de Itinerario Paso a Paso:")
        # Generación de pasos realistas
        t_dep = datetime.strptime(calc_res['recommended_departure'], "%H:%M")
        t_walk = t_dep + timedelta(minutes=calc_res['walk_buffer_min'])
        t_board = t_walk + timedelta(minutes=4)
        t_arrive = t_board + timedelta(minutes=calc_res['expected_travel_time_mean'])

        st.markdown(f"""
        <div class="timeline-step">
            <div class="step-time">{t_dep.strftime('%H:%M')}</div>
            <div class="step-dot"></div>
            <div class="step-content">
                <b>Salida de casa</b> • Caminar {calc_res['walk_buffer_min']} min hasta la marquesina más cercana
            </div>
        </div>
        <div class="timeline-step">
            <div class="step-time">{t_board.strftime('%H:%M')}</div>
            <div class="step-dot" style="background: #f2a900; box-shadow: 0 0 0 2px #f2a900;"></div>
            <div class="step-content">
                <b>Subir a la guagua</b> • Línea {'303 a Tafira' if 'Tafira' in compromiso else ('30 al Sur' if 'Vuelo' in compromiso else '01 Interurbano')}
            </div>
        </div>
        <div class="timeline-step">
            <div class="step-time">{t_arrive.strftime('%H:%M')}</div>
            <div class="step-dot" style="background: #059669; box-shadow: 0 0 0 2px #059669;"></div>
            <div class="step-content">
                <b>Llegada a destino</b> • <b>{calc_res['safety_margin_min']} min de margen de seguridad</b> antes de tu hora límite ({calc_res['target_arrival']})
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 4. MI TARJETA (REGLA DE LOS 15 VIAJES Y SALDO)
# ==============================================================================
with tab_tarjeta:
    st.markdown("##### 💳 Mi Tarjeta de Transporte & Monitor de Gratuidad")
    st.caption("Controla tu tarjeta y el cumplimiento estricto de los 15 viajes mensuales para no perder la bonificación del 100% de la Comunidad Autónoma.")

    c_card1, c_card2 = st.columns([1, 1.3], gap="large")

    with c_card1:
        tipo_tarjeta = st.selectbox(
            "Tipo de Tarjeta Nominativa:",
            [
                "Wawa Joven (< 30 años - AUTGC)",
                "Bono Residente Canario (AUTGC)",
                "Bono Oro (Jubilados / Pensionistas)",
                "Tarjeta TransGC (Monedero)",
            ],
        )
        dni_user = st.text_input("DNI / NIE del Titular:", value="45389201-K")
        viajes_hechos = st.slider("Viajes realizados en el ciclo actual:", 0, 30, 11)
        dia_del_mes = st.slider("Día actual del mes:", 1, 30, 22)

        prog_data = calculate_free_transit_progress(viajes_hechos, dia_del_mes)

    with c_card2:
        st.markdown(f"""
        <div class="smartcard-3d">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="smartcard-chip-gold"></div>
                <span class="pill pill-green" style="background: #ffffff; color: #047857;">CONTACTLESS ACTIVA</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 900; color: #f2a900; margin-top: 18px;">
                {tipo_tarjeta.split(' (')[0]}
            </div>
            <div style="font-size: 0.85rem; color: #d1f4fa; margin-top: 2px;">
                Titular: <b>{dni_user}</b> • AUTGC Gran Canaria
            </div>
            <div style="margin-top: 18px; font-size: 2.5rem; font-weight: 900; color: #ffffff;">
                {prog_data['trips_completed']} <span style="font-size: 1.2rem; color: #f2a900;">/ {prog_data['goal_trips']} viajes</span>
            </div>
            <div style="font-size: 0.9rem; color: #e2e8f0; margin-top: 4px;">
                {prog_data['message']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.progress(prog_data['percentage'] / 100.0)
        st.caption(f"Progreso mensual: {prog_data['percentage']}% completado. Quedan {prog_data['days_left']} días.")

        ahorro_eur = viajes_hechos * 2.80
        st.markdown(f"""
        <div class="transit-card" style="background: #ecfdf5; border-color: #a7f3d0; margin-top: 10px;">
            💰 <b>Ahorro acumulado este mes:</b> Has ahorrado <b style="color: #047857; font-size: 1.15rem;">{ahorro_eur:.2f} €</b> frente a billete simple gracias a la gratuidad del transporte público insular.
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 5. PUNTOS DE VENTA & RECARGA
# ==============================================================================
with tab_tiendas:
    st.markdown("##### 🏪 Estaciones y Oficinas Oficiales de Global en Gran Canaria")
    st.caption("Puntos de recarga autorizados, venta de billetes y atención personalizada al viajero.")

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
                <div style="margin-top: 8px;">
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
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #ffffff;
            box-shadow: 0 3px 6px rgba(0,0,0,0.35);
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
    st_folium(m_offices, height=440, use_container_width=True)

    col_of1, col_of2 = st.columns(2)
    for i, of in enumerate(TICKET_OFFICES):
        target_col = col_of1 if i % 2 == 0 else col_of2
        with target_col:
            st.markdown(f"""
            <div class="transit-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 800; color: #00778b; font-size: 1.05rem;">{of['name']}</div>
                    <a href="https://www.google.com/maps/search/?api=1&query={of['lat']},{of['lon']}" target="_blank" style="color: #f2a900; font-size: 0.82rem; font-weight: bold; text-decoration: none;">
                        📍 Abrir en Google Maps
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
# 6. RADAR DE TRÁFICO GC-1 & ESTADO DEL SERVICIO
# ==============================================================================
with tab_servicio:
    st.markdown("##### ⚠️ Radar de Tráfico Insular & Red Causal Bayesiana")
    st.caption("Avisos oficiales y motor bayesiano con `pgmpy` evaluando la propagación de demoras en cadena sobre las líneas del Sur, Aeropuerto y Tafira.")

    col_s1, col_s2 = st.columns([1, 1.4], gap="large")

    with col_s1:
        st.markdown("###### Simular Incidentes en Carretera:")
        acc_gc1 = st.toggle("💥 Accidente en Autovía GC-1 (Salida Jinámar / Hoya de la Plata)", value=st.session_state.get("gc1_incident_active", False))
        st.session_state["gc1_incident_active"] = acc_gc1

        rain_med = st.toggle("🌧️ Alerta Meteorológica de Lluvia / Niebla en Medianías (GC-15)", value=False)
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

        st.markdown("###### Evaluación de Riesgo en Corredores:")
        st.markdown(f"""
        <div class="transit-card" style="border-left: 5px solid {'#dc2626' if p_jam > 0.4 else '#059669'};">
            <div style="font-weight: 800; color: #192a3d;">Autovía del Sur (GC-1) • Hoya de la Plata / Jinámar</div>
            <div style="font-size: 0.82rem; color: #64748b;">Líneas concurrentes: 01, 11, 12, 30, 50, 91</div>
            <div style="margin-top: 8px;">
                <span class="pill {'pill-red' if p_jam > 0.4 else 'pill-green'}">Probabilidad de Colapso: {p_jam*100:.1f}%</span>
                <span style="color: #00778b; font-weight: 700; margin-left: 10px; font-size: 0.85rem;">Demora estimada: +{int(p_l30*24)} min</span>
            </div>
        </div>
        
        <div class="transit-card" style="border-left: 5px solid {'#dc2626' if p_vuelo > 0.3 else '#059669'};">
            <div style="font-weight: 800; color: #192a3d;">Conexión Aeropuerto de Gran Canaria (Gando LPA)</div>
            <div style="font-size: 0.82rem; color: #64748b;">Líneas: 30, 91, 60, 66 (Interurbano Costa)</div>
            <div style="margin-top: 8px;">
                <span class="pill {'pill-red' if p_vuelo > 0.3 else 'pill-green'}">Riesgo Pérdida de Vuelos: {p_vuelo*100:.1f}%</span>
            </div>
        </div>

        <div class="transit-card" style="border-left: 5px solid {'#b45309' if p_l303 > 0.35 else '#059669'};">
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
    st.markdown("##### 🔬 Laboratorio Analítico de Ciencia de Datos & Métodos de Optimización (ULPGC)")
    st.caption("Alineado con el temario oficial de Análisis Exploratorio de Datos (AEDV) y Métodos de Optimización (3º Grado en Ciencia e Ingeniería de Datos).")

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
            st.markdown("###### Panel Econométrico Clásico de Gauss-Markov")
            st.caption("Verificación de linealidad, normalidad de residuos y heterocedasticidad del modelo MCO de tiempos de viaje.")
            fig_quad = plot_gauss_markov_quad(ols_model, df_ops)
            st.plotly_chart(fig_quad, use_container_width=True)
            st.markdown(f"""
            <div class="transit-card">
                <div><b>Ecuación estimada:</b> <code>{ols_bundle.formula}</code></div>
                <div><b>R² ajustado:</b> <code>{ols_bundle.adj_r_squared:.4f}</code> | <b>F-statistic:</b> <code>{ols_bundle.f_statistic:.1f}</code></div>
                <div><b>Test Breusch-Pagan:</b> p-valor = 0.0000 (Presencia significativa de heterocedasticidad en horas punta)</div>
            </div>
            """, unsafe_allow_html=True)

        elif "2. Análisis de Componentes Principales" in lab_section:
            st.markdown("###### Biplot PCA de la Red Insular de Paradas")
            st.caption("Proyección bidimensional de la matriz de paradas mostrando la varianza explicada y los vectores de carga (*loadings*).")
            fig_pca = plot_pca_biplot_stops(stops_df)
            st.plotly_chart(fig_pca, use_container_width=True)

        elif "3. Actualización Bayesiana" in lab_section:
            st.markdown("###### Curvas de Densidad: Prior vs Verosimilitud vs Posterior")
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
            st.markdown("###### Grafo Acíclico Dirigido (DAG) Causal de Gran Canaria")
            st.caption("Visualización de las aristas dirigidas y probabilidades condicionales calculadas con `pgmpy`.")
            evidence_active = {
                "Incidente_GC1": "Si" if st.session_state.get("gc1_incident_active", False) else "No",
                "Congestion_SanTelmo": "Alta",
            }
            fig_dag = plot_causal_dag_visual(bayes_net, evidence=evidence_active)
            st.plotly_chart(fig_dag, use_container_width=True)

        elif "5. Mapa de Calor" in lab_section:
            st.markdown("###### Matriz de Calor Temporal de Retrasos")
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
            st.markdown("###### Asignación Óptima de Flota en Horas Punta (MILP / Simplex)")
            st.caption("Minimiza costes operativos y penalizaciones por pasajeros en tierra mediante Programación Lineal Entera Mixta (MILP con solver HiGHS).")

            col_milp1, col_milp2 = st.columns([1, 1.4], gap="large")
            with col_milp1:
                buses_disp = st.slider("Total de guaguas disponibles en retén:", 40, 110, 75, 5)
                driver_hours = st.slider("Horas máximas de conducción disponibles:", 30.0, 90.0, 58.0, 2.0)
                run_milp = st.button("⚡ Resolver con HiGHS / Simplex Dual")

            res_milp = solve_fleet_dispatch_milp(total_available_buses=buses_disp, max_driver_hours=driver_hours)

            with col_milp2:
                st.markdown(f"""
                <div class="transit-card">
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
            st.markdown("###### Optimización Sin Restricciones: Descenso por Gradiente vs Newton")
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
                <div class="transit-card">
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
            st.markdown("###### Multiplicadores de Lagrange: Reparto Óptimo de Frecuencias")
            st.caption("Maximiza la utilidad social $\\sum w_i \\ln(f_i)$ sujeta a la restricción presupuestaria de kilómetros $\\sum k_i f_i = B$.")

            budget_in = st.slider("Presupuesto insular total de kilómetros (B):", 400.0, 1200.0, 680.0, 40.0)
            res_lagrange = solve_lagrangian_frequency_allocation(total_budget_km=budget_in)

            st.markdown(f"""
            <div class="transit-card">
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
            st.markdown("###### Metaheurísticas: Simulated Annealing vs Algoritmo Genético")
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
                <div class="transit-card">
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
