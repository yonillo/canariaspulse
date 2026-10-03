"""GUAGUAS CANARIAS 2.0: Sistema Inteligente de Transporte de Gran Canaria (LPA & GLOBAL).

Inspirada en la excelencia y funcionalidad de la app GuaguasLPA (Guaguas Municipales)
y fusionada con la red insular de Global (Salcai Utinsa S.A.):
1. 🚏 ¿Cuánto Falta? (Tiempo real por parada, buscador de postes, semáforo de ocupación Poisson).
2. 🗺️ Mapa en Vivo (Google Maps oficial con flota GPS y autopistas GC-1, GC-2 y GC-110).
3. 🧭 Cómo Llegar (Planificador de rutas multimodal con Garantía Bayesiana 95% para exámenes y vuelos).
4. 📋 Líneas y Recorridos (Trazados completos en Ida y Vuelta con tiempos parada a parada).
5. 📲 Bono Virtual & QR (Wawa Joven / Bono Residente con generación de QR para canceladora, regla 15 viajes y recarga).
6. ⚠️ Avisos de Servicio (Feed en directo de incidencias en GC-1, refuerzos universitarios y eventos).
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
    plot_bayesian_update_curve = getattr(vd, "plot_bayesian_update_curve", None)
    plot_causal_dag_visual = getattr(vd, "plot_causal_dag_visual", None)
    plot_delay_heatmap = getattr(vd, "plot_delay_heatmap", None)
    plot_gauss_markov_quad = getattr(vd, "plot_gauss_markov_quad", None)
    plot_milp_dispatch_bars = getattr(vd, "plot_milp_dispatch_bars", None)
    plot_pca_biplot_stops = getattr(vd, "plot_pca_biplot_stops", None)
    plot_unconstrained_convergence = getattr(vd, "plot_unconstrained_convergence", None)
    plot_heuristic_convergence = getattr(vd, "plot_heuristic_convergence", None)

if plot_heuristic_convergence is None:
    def plot_heuristic_convergence(sa_history: list, ga_history: list) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(sa_history))), y=sa_history, mode='lines', name='Simulated Annealing (Metropolis 2-opt)', line=dict(color='#002b49', width=2)))
        fig.add_trace(go.Scatter(x=np.linspace(0, len(sa_history), len(ga_history)), y=ga_history, mode='lines+markers', name='Algoritmo Genético (OX + Elitismo)', line=dict(color='#ffd100', width=2.5), marker=dict(size=4)))
        fig.update_layout(title="Optimización de Rutas Insulares (TSP): SA vs AG", paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc', font=dict(color='#002b49'), height=380, margin=dict(l=20, r=20, t=40, b=20))
        return fig

if plot_unconstrained_convergence is None:
    def plot_unconstrained_convergence(gd_losses: list, newton_losses: list) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(gd_losses))), y=gd_losses, mode='lines+markers', name='Descenso por Gradiente (Lineal)', line=dict(color='#ffd100', width=2.5), marker=dict(size=4)))
        fig.add_trace(go.Scatter(x=list(range(len(newton_losses))), y=newton_losses, mode='lines+markers', name='Método de Newton (Cuadrático)', line=dict(color='#002b49', width=3), marker=dict(size=8, symbol='diamond')))
        fig.update_layout(title="Convergencia en Calibración de Congestión (BPR)", yaxis_type="log", paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc', font=dict(color='#002b49'), height=380, margin=dict(l=20, r=20, t=40, b=20))
        return fig

if plot_milp_dispatch_bars is None:
    def plot_milp_dispatch_bars(served: dict, unmet: dict, dispatches: dict = None) -> go.Figure:
        corridors = [str(c).split(" (")[0] for c in served.keys()]
        served_vals = list(served.values())
        unmet_vals = list(unmet.values())
        fig = go.Figure()
        fig.add_trace(go.Bar(x=corridors, y=served_vals, name='Pasajeros Atendidos (65 pax/bus)', marker_color='#002b49', text=served_vals, textposition='auto'))
        fig.add_trace(go.Bar(x=corridors, y=unmet_vals, name='Demanda Desatendida', marker_color='#ef4444', text=unmet_vals, textposition='auto'))
        fig.update_layout(barmode='stack', title="Asignación Óptima de Capacidad y Demanda (MILP / Simplex)", paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc', font=dict(color='#002b49'), height=380, margin=dict(l=20, r=20, t=40, b=20))
        return fig

from src.bayesian.bayesian_network import GranCanariaBayesianNetwork
from src.bayesian.bayesian_regression import BayesianLinearRegressor
from src.bayesian.clustering_gmm import fit_gmm_stop_clustering
from src.core_stats.linear_regression import fit_travel_time_ols
from src.data_ingestion.extract_network import get_curated_network, KEY_HUBS
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
    generate_virtual_card_qr,
    get_network_lines_catalog,
    get_live_service_alerts,
    plan_multimodal_trip,
)

# Configuración de página
st.set_page_config(
    page_title="GuaguasLPA & GLOBAL | Gran Canaria Smart Transit",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilo visual de alta gama: Modern Mobile Transit App UI (Inspirado en GuaguasLPA + Global)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

    :root {
        --guaguas-yellow: #ffd100;
        --guaguas-yellow-dark: #f59e0b;
        --guaguas-navy: #002b49;
        --guaguas-navy-dark: #001a2c;
        --global-teal: #00778b;
        --global-blue: #0284c7;
        --bg-color: #f1f5f9;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --border-color: #e2e8f0;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-main);
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Cabecera Estilo App Móvil GuaguasLPA */
    .app-header {
        background: linear-gradient(135deg, #002b49 0%, #001a2c 100%);
        border-bottom: 4px solid var(--guaguas-yellow);
        padding: 18px 24px;
        border-radius: 20px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 43, 73, 0.25);
    }

    .app-header-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    .app-logo-box {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .app-logo-badge {
        background: var(--guaguas-yellow);
        color: #002b49;
        font-size: 1.8rem;
        font-weight: 900;
        padding: 6px 14px;
        border-radius: 12px;
        letter-spacing: -0.5px;
        box-shadow: 0 4px 10px rgba(255, 209, 0, 0.3);
    }

    .app-title-group h1 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
    }

    .app-title-group p {
        margin: 2px 0 0 0;
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
    }

    .app-status-pills {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .live-pill {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
        animation: pulseDot 1.8s infinite;
    }

    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* Badges de Líneas estilo Guaguas Municipales / Global */
    .line-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        border-radius: 10px;
        padding: 6px 12px;
        min-width: 52px;
        font-size: 1.15rem;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.12);
        letter-spacing: -0.5px;
    }

    .line-badge-yellow { background: var(--guaguas-yellow); color: #002b49; }
    .line-badge-teal { background: #00778b; color: #ffffff; }
    .line-badge-blue { background: #0284c7; color: #ffffff; }
    .line-badge-navy { background: #002b49; color: #ffd100; border: 1px solid #ffd100; }
    .line-badge-green { background: #10b981; color: #ffffff; }

    /* Tarjetas de Guagua en Parada */
    .bus-arrival-card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        padding: 16px 20px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .bus-arrival-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 43, 73, 0.08);
        border-color: #cbd5e1;
    }

    .arrival-countdown-box {
        text-align: right;
        min-width: 100px;
    }

    .arrival-minutes {
        font-size: 1.55rem;
        font-weight: 900;
        color: #002b49;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }

    .arrival-subtext {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 600;
    }

    /* Marquesina Digital LED */
    .led-marquesina {
        background: #000000;
        border: 3px solid #1e293b;
        border-radius: 14px;
        padding: 14px 18px;
        font-family: 'Courier New', Courier, monospace;
        color: #ffb800;
        box-shadow: inset 0 0 15px rgba(255, 184, 0, 0.2), 0 8px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 18px;
    }

    /* Tarjeta Wawa Joven / Bono Residente */
    .smartcard-3d {
        background: linear-gradient(135deg, #002b49 0%, #004d7a 50%, #00778b 100%);
        border-radius: 20px;
        padding: 24px;
        color: #ffffff;
        box-shadow: 0 20px 35px -10px rgba(0, 43, 73, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    .smartcard-3d::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(255, 209, 0, 0.2) 0%, transparent 70%);
        pointer-events: none;
    }

    /* Itinerario Timeline */
    .timeline-item {
        display: flex;
        gap: 16px;
        padding-bottom: 18px;
        position: relative;
    }

    .timeline-item:not(:last-child)::before {
        content: "";
        position: absolute;
        left: 17px;
        top: 36px;
        bottom: 0;
        width: 2px;
        background: #cbd5e1;
    }

    .timeline-icon-box {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        z-index: 1;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 8px 12px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        font-weight: 700;
        font-size: 0.92rem;
        border-radius: 10px;
        color: #475569;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #002b49 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0, 43, 73, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 1. CABECERA PRINCIPAL TIPO GUAGUASLPA
current_time_str = datetime.now().strftime("%H:%M")
st.markdown(f"""
<div class="app-header">
    <div class="app-header-top">
        <div class="app-logo-box">
            <div class="app-logo-badge">GLPA</div>
            <div class="app-title-group">
                <h1>GUAGUAS CANARIAS • LPA & GLOBAL</h1>
                <p>Red Insular y Metropolitana Inteligente de Gran Canaria</p>
            </div>
        </div>
        <div class="app-status-pills">
            <div class="live-pill">
                <span class="live-dot"></span>
                <span>TELEMETRÍA GPS ACTIVA (1s)</span>
            </div>
            <div style="background: rgba(255,209,0,0.2); border: 1px solid rgba(255,209,0,0.5); color: #ffd100; font-size: 0.78rem; font-weight: 800; padding: 5px 12px; border-radius: 20px;">
                💳 BONO ACTIVO: YONE SUÁREZ
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. SELECTOR DE VISTA (Móvil vs Pantalla Completa)
col_view1, col_view2 = st.columns([8, 2])
with col_view2:
    view_mode = st.selectbox("Formato de pantalla", ["💻 Pantalla Completa", "📱 Modo Móvil (Estilo App)"], label_visibility="collapsed")

# 3. PESTAÑAS PRINCIPALES DE LA APP
tab_wait, tab_map, tab_plan, tab_lines, tab_card, tab_alerts, tab_lab = st.tabs([
    "🚏 ¿Cuánto Falta?",
    "🗺️ Mapa en Vivo",
    "🧭 Cómo Llegar",
    "📋 Líneas y Recorridos",
    "📲 Bono Virtual & QR",
    "⚠️ Avisos de Servicio",
    "🔬 Laboratorio & Optimización",
])

# ==============================================================================
# PESTAÑA 1: 🚏 ¿CUÁNTO FALTA? (Tiempo real por parada estilo GuaguasLPA)
# ==============================================================================
with tab_wait:
    st.markdown("### 🚏 Consulta en Tiempo Real por Parada")
    st.markdown("Introduce el código de la parada para ver al instante las guaguas en aproximación con su ocupación real.")

    # Acceso rápido a paradas frecuentes
    st.markdown("**⭐ Accesos Rápidos Frecuentes:**")
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    
    # Control de estado de parada seleccionada
    if "current_stop_code" not in st.session_state:
        st.session_state.current_stop_code = "1001"

    if col_f1.button("🏢 San Telmo (1001)", use_container_width=True):
        st.session_state.current_stop_code = "1001"
    if col_f2.button("🌴 Sta. Catalina (1002)", use_container_width=True):
        st.session_state.current_stop_code = "1002"
    if col_f3.button("🎓 Campus Tafira (2015)", use_container_width=True):
        st.session_state.current_stop_code = "2015"
    if col_f4.button("✈️ Aeropuerto LPA (4001)", use_container_width=True):
        st.session_state.current_stop_code = "4001"
    if col_f5.button("🏖️ Maspalomas (5020)", use_container_width=True):
        st.session_state.current_stop_code = "5020"

    # Buscador directo por código o nombre
    stop_options = [f"{s['stop_code']} - {s['name']}" for s in OFFICIAL_STOPS]
    current_index = 0
    for idx, opt in enumerate(stop_options):
        if opt.startswith(st.session_state.current_stop_code):
            current_index = idx
            break

    selected_stop_raw = st.selectbox(
        "Buscar parada por código o nombre:",
        stop_options,
        index=current_index,
        label_visibility="visible"
    )
    selected_stop_code = selected_stop_raw.split(" - ")[0].strip()
    selected_stop_info = search_stop_by_code(selected_stop_code)

    if selected_stop_info:
        # Ficha oficial de parada
        st.markdown(f"""
        <div style="background: #ffffff; border-radius: 16px; border: 2px solid #002b49; padding: 18px 22px; margin: 16px 0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(0,43,73,0.06);">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: #002b49; color: #ffd100; font-size: 1.5rem; font-weight: 900; padding: 10px 16px; border-radius: 12px; letter-spacing: -0.5px;">
                    🚏 {selected_stop_info['stop_code']}
                </div>
                <div>
                    <h3 style="margin: 0; color: #002b49; font-size: 1.25rem; font-weight: 800;">{selected_stop_info['name']}</h3>
                    <p style="margin: 3px 0 0 0; color: #64748b; font-size: 0.88rem; font-weight: 600;">
                        Zona: {selected_stop_info.get('zone', 'Gran Canaria')} • Altitud: {selected_stop_info.get('altitude', 15)} msnm
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background: #ecfdf5; border: 1px solid #10b981; color: #065f46; font-size: 0.8rem; font-weight: 700; padding: 6px 12px; border-radius: 20px;">
                    📶 Pantalla LED Conectada
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Marquesina digital interactiva
        now_dt = datetime.now()
        departures = get_live_departures_for_hub(
            stop_id="hub-01",
            hour=now_dt.hour,
            minute=now_dt.minute,
            is_weekend=now_dt.weekday() >= 5
        )

        st.markdown("#### 🚌 Próximas Llegadas a esta Parada")

        # Inyectar tarjetas individuales de llegada idénticas a GuaguasLPA
        badge_styles = {
            "303": ("line-badge-yellow", "Universidad / Medianías"),
            "30": ("line-badge-teal", "Sur Turístico"),
            "91": ("line-badge-blue", "Expreso Autopista"),
            "103": ("line-badge-navy", "Norte Costa"),
            "01": ("line-badge-green", "Ruta General Sur"),
            "12": ("line-badge-yellow", "Puerto - Hoya de la Plata"),
        }

        for dep in departures:
            line_str = dep.route_short_name
            style_cls, corridor_desc = badge_styles.get(line_str, ("line-badge-navy", "Servicio Regular"))
            
            # Badge de ocupación Poisson
            if "🟢" in dep.crowding_level:
                crowd_bg = "#ecfdf5"
                crowd_border = "#10b981"
                crowd_text = "#047857"
            elif "🟡" in dep.crowding_level:
                crowd_bg = "#fffbeb"
                crowd_border = "#f59e0b"
                crowd_text = "#b45309"
            else:
                crowd_bg = "#fef2f2"
                crowd_border = "#ef4444"
                crowd_text = "#b91c1c"

            pulse_style = 'animation: pulseDot 1s infinite;' if dep.minutes_to_arrival_min <= 3 else ''

            st.markdown(f"""
            <div class="bus-arrival-card">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div class="line-badge {style_cls}">
                        {line_str}
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.15rem; font-weight: 800; color: #002b49;">{dep.destination}</span>
                        </div>
                        <div style="margin-top: 4px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <span style="background: {crowd_bg}; border: 1px solid {crowd_border}; color: {crowd_text}; font-size: 0.78rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">
                                {dep.crowding_level} ({dep.passengers_estimate} pax)
                            </span>
                            <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">♿ PMR • 🍃 Cero Emisiones • 📶 Wi-Fi</span>
                        </div>
                    </div>
                </div>
                <div class="arrival-countdown-box">
                    <div class="arrival-minutes" style="color: {'#10b981' if dep.minutes_to_arrival_min <= 3 else '#002b49'}; {pulse_style}">
                        {dep.minutes_to_arrival_min} min
                    </div>
                    <div class="arrival-subtext">Paso: {dep.expected_arrival_time}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Botón de simulación de aviso
        col_nt1, col_nt2 = st.columns([8, 2])
        with col_nt2:
            if st.button("🔔 Avisarme cuando esté a 5 min", use_container_width=True):
                st.success("✅ Alerta activada: Recibirás una notificación cuando tu guagua esté a 5 minutos de la parada.")

# ==============================================================================
# PESTAÑA 2: 🗺️ MAPA EN VIVO (Google Maps Oficial)
# ==============================================================================
with tab_map:
    st.markdown("### 🗺️ Radar en Vivo sobre Google Maps Oficial")
    st.markdown("Visualización en tiempo real de paradas oficiales, autopistas insulares y guaguas GPS en circulación activa.")

    col_m1, col_m2, col_m3 = st.columns([4, 4, 2])
    with col_m1:
        map_layer_type = st.radio("Capa de Google Maps:", ["Google Carreteras / Calles", "Google Satélite Híbrido"], horizontal=True)
    with col_m2:
        filter_corridor = st.selectbox("Filtrar por corredor insular:", ["Todos los corredores", "GC-1 Sur Turístico", "GC-110 Centro / Campus Tafira", "GC-2 Norte"], label_visibility="visible")
    with col_m3:
        st.metric("Guaguas en Circulación", "18 activas", delta="100% flota conectada")

    # URL oficial de tiles de Google Maps
    if map_layer_type == "Google Satélite Híbrido":
        google_tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    else:
        google_tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"

    # Crear mapa con Folium centrado en Gran Canaria
    fmap = folium.Map(
        location=[28.0000, -15.4800],
        zoom_start=11,
        tiles=google_tile_url,
        attr="Google Maps & Global Salcai Utinsa",
    )

    # 1. Trazado de Carreteras
    for poly in HIGHWAY_POLYLINES:
        rgb_color = poly["color"][:3]
        hex_color = f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
        latlngs = [[pt[1], pt[0]] for pt in poly["path"]]
        folium.PolyLine(
            locations=latlngs,
            color=hex_color,
            weight=poly["width"],
            opacity=0.85,
            tooltip=poly["name"]
        ).add_to(fmap)

    # 2. Marcadores de Paradas
    for stop in OFFICIAL_STOPS:
        gmaps_link = f"https://www.google.com/maps/search/?api=1&query={stop['lat']},{stop['lon']}"
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 180px;">
            <b style="color: #002b49; font-size: 14px;">🚏 Parada {stop['stop_code']}</b><br/>
            <span>{stop['name']}</span><br/>
            <small style="color: #64748b;">Zona: {stop.get('zone', 'GC')}</small><br/>
            <hr style="margin: 6px 0; border: none; border-top: 1px solid #e2e8f0;"/>
            <a href="{gmaps_link}" target="_blank" style="color: #00778b; font-weight: bold; text-decoration: none;">📍 Abrir en Google Maps</a>
        </div>
        """
        folium.CircleMarker(
            location=[stop["lat"], stop["lon"]],
            radius=6 if stop["is_hub"] else 4,
            color="#002b49",
            fill=True,
            fill_color="#ffd100" if stop["is_hub"] else "#00778b",
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"Parada {stop['stop_code']}: {stop['name']}"
        ).add_to(fmap)

    # 3. Flota de Guaguas GPS en Movimiento
    live_fleet = get_live_simulated_fleet()
    for _, bus in live_fleet.iterrows():
        line_num = str(bus["line"])
        bus_id = str(bus["bus_id"])
        dest = str(bus["destination"])
        speed = int(bus["speed_kmh"])
        occ = int(bus["occupancy_pct"])
        crowd_label = "🟢 Baja" if occ < 60 else ("🟡 Media" if occ < 85 else "🔴 Alta")

        bus_popup = f"""
        <div style="font-family: sans-serif; min-width: 190px;">
            <b style="background: #ffd100; color: #002b49; padding: 2px 6px; border-radius: 4px; font-size: 13px;">Línea {line_num}</b>
            <b style="color: #002b49; margin-left: 6px;">Guagua #{bus_id}</b><br/>
            <div style="margin-top: 6px;">
                <b>Destino:</b> {dest}<br/>
                <b>Velocidad:</b> {speed} km/h<br/>
                <b>Ocupación:</b> {crowd_label} ({occ}%)
            </div>
        </div>
        """
        folium.Marker(
            location=[float(bus["lat"]), float(bus["lon"])],
            popup=folium.Popup(bus_popup, max_width=260),
            icon=folium.DivIcon(
                html=f"""
                <div style="background: #002b49; color: #ffd100; border: 2px solid #ffffff; font-weight: 900; font-size: 11px; border-radius: 8px; padding: 2px 6px; box-shadow: 0 3px 6px rgba(0,0,0,0.3); text-align: center; white-space: nowrap;">
                    🚌 {line_num}
                </div>
                """
            ),
            tooltip=f"Línea {line_num} ➔ {dest} ({speed} km/h)"
        ).add_to(fmap)

    # Renderizar mapa
    st_folium(fmap, width="100%", height=520, returned_objects=[])

# ==============================================================================
# PESTAÑA 3: 🧭 CÓMO LLEGAR (Planificador de Rutas Multimodal)
# ==============================================================================
with tab_plan:
    st.markdown("### 🧭 Planificador de Rutas Multimodal Inteligente")
    st.markdown("Calcula las mejores combinaciones de viaje con **Garantía Bayesiana del 95%** para que nunca llegues tarde a un examen en Tafira o a un vuelo en el Aeropuerto.")

    col_p1, col_p2, col_p3 = st.columns([4, 4, 3])
    with col_p1:
        origin_choice = st.selectbox(
            "Origen:",
            ["Estación San Telmo (1001)", "Intercambiador Santa Catalina (1002)", "Vega de San Mateo (2201)", "Maspalomas Faro (5020)"],
            index=0
        )
    with col_p2:
        dest_choice = st.selectbox(
            "Destino:",
            ["Campus Universitario Tafira (2015)", "Aeropuerto de Gran Canaria LPA (4001)", "Estación de Gáldar (7020)", "Puerto de Mogán (6015)"],
            index=0
        )
    with col_p3:
        target_arrival = st.time_input("Hora requerida de llegada:", time(8, 45))

    priority_opt = st.radio(
        "Criterio de optimización de viaje:",
        ["⭐ Garantía Bayesiana 95% (Examen / Vuelo)", "⚡ Ruta Más Rápida", "💺 Confort (Asiento Garantizado)"],
        horizontal=True
    )

    # Calcular opciones detalladas
    itineraries = plan_multimodal_trip(
        origin_name=origin_choice.split("(")[0].strip(),
        destination_name=dest_choice.split("(")[0].strip(),
        arrival_time_str=target_arrival.strftime("%H:%M"),
        priority=priority_opt,
        incident_active=False
    )

    st.markdown(f"#### 🎯 Opciones de Viaje para llegar a las **{target_arrival.strftime('%H:%M')}**")

    for opt in itineraries:
        with st.container():
            st.markdown(f"""
            <div style="background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(0,43,73,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
                    <div>
                        <span style="background: {opt['badge_color']}; color: #ffffff; font-weight: 800; font-size: 0.8rem; padding: 4px 10px; border-radius: 20px;">
                            {opt['badge']}
                        </span>
                        <h4 style="margin: 6px 0 0 0; color: #002b49; font-size: 1.15rem; font-weight: 800;">{opt['title']}</h4>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.4rem; font-weight: 900; color: #002b49;">⏱️ {opt['duration_min']} min</span>
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Salida recomendada: <b>{opt['departure_time']}</b></div>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; margin-bottom: 14px;">
                    <span style="background: #f1f5f9; color: #334155; font-size: 0.78rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">{opt['crowding']}</span>
                    <span style="background: #f1f5f9; color: #334155; font-size: 0.78rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">🛡️ Colchón de seguridad: {opt['safety_buffer_min']} min</span>
                    <span style="background: #f1f5f9; color: #334155; font-size: 0.78rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">🔄 {opt['transfers']} transbordos</span>
                </div>
                <div style="border-top: 1px solid #f1f5f9; padding-top: 12px;">
            """, unsafe_allow_html=True)

            for step in opt["steps"]:
                st.markdown(f"""
                <div style="display: flex; gap: 12px; margin-bottom: 8px; align-items: flex-start;">
                    <span style="font-size: 1.1rem;">{step['icon']}</span>
                    <span style="font-size: 0.9rem; color: #334155; font-weight: 500;">{step['text']}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

# ==============================================================================
# PESTAÑA 4: 📋 LÍNEAS Y RECORRIDOS (Ida y Vuelta)
# ==============================================================================
with tab_lines:
    st.markdown("### 📋 Líneas Troncales, Recorridos y Horarios")
    st.markdown("Consulta el trazado completo parada por parada en ambos sentidos (Ida / Vuelta) como en GuaguasLPA.")

    catalog = get_network_lines_catalog()
    line_names = [f"Línea {l['line']} - {l['name']}" for l in catalog]
    selected_line_idx = st.selectbox("Selecciona una línea:", list(range(len(line_names))), format_func=lambda i: line_names[i])
    line_data = catalog[selected_line_idx]

    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.metric("Frecuencia Media", line_data["frequency"])
    col_l2.metric("Horario Operativo", line_data["operating_hours"])
    col_l3.metric("Distancia de Ruta", f"{line_data['distance_km']} km")
    col_l4.metric("Tiempo Medio Trayecto", f"{line_data['mean_duration_min']} min")

    direction = st.radio("Sentido de circulación:", ["➡️ Sentido Ida", "⬅️ Sentido Vuelta"], horizontal=True)
    stops_list = line_data["stops_ida"] if "Ida" in direction else line_data["stops_vuelta"]

    st.markdown(f"#### 🚏 Itinerario de Paradas ({direction})")

    for i, s in enumerate(stops_list):
        is_first = (i == 0)
        is_last = (i == len(stops_list) - 1)
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-icon-box" style="background: {'#002b49' if is_first or is_last else '#e2e8f0'}; color: {'#ffd100' if is_first or is_last else '#64748b'};">
                {'🚩' if is_first else ('🏁' if is_last else '🚏')}
            </div>
            <div style="flex-grow: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #002b49; font-size: 0.95rem;">Parada {s['code']}: {s['name']}</b>
                    <span style="background: #f1f5f9; color: #475569; font-size: 0.78rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{s['time']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# PESTAÑA 5: 📲 BONO VIRTUAL & QR (La estrella de GuaguasLPA)
# ==============================================================================
with tab_card:
    st.markdown("### 📲 Tarjeta Virtual Wawa Joven & Bono Residente Canario")
    st.markdown("Lleva tu bono en el móvil, genera tu **código QR de embarque** para la canceladora y controla la regla de los **15 viajes** del Gobierno de Canarias.")

    col_c1, col_c2 = st.columns([5, 5])

    with col_c1:
        # Tarjeta Virtual 3D
        st.markdown(f"""
        <div class="smartcard-3d">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
                <div>
                    <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.8;">GOBIERNO DE CANARIAS • CABILDO DE GRAN CANARIA</span>
                    <h3 style="margin: 4px 0 0 0; font-size: 1.4rem; font-weight: 800; color: #ffd100;">WAWA JOVEN • 100% GRATUIDAD</h3>
                </div>
                <div style="font-size: 1.6rem;">📶</div>
            </div>
            <div style="margin-bottom: 24px;">
                <div style="width: 44px; height: 32px; background: linear-gradient(135deg, #d4af37 0%, #f9d976 100%); border-radius: 6px; box-shadow: inset 0 0 4px rgba(0,0,0,0.3); margin-bottom: 14px;"></div>
                <span style="font-family: monospace; font-size: 1.25rem; letter-spacing: 2px; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">
                    3500 1928 4022 8841
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <div>
                    <span style="font-size: 0.7rem; opacity: 0.75; text-transform: uppercase;">TITULAR</span>
                    <div style="font-weight: 800; font-size: 0.95rem; letter-spacing: 0.5px;">YONE SUÁREZ VIERA</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.7rem; opacity: 0.75; text-transform: uppercase;">CADUCIDAD</span>
                    <div style="font-weight: 800; font-size: 0.95rem;">10/2028</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Botón para generar QR de Validación
        if st.button("📲 Generar Código QR para Subir a la Guagua", use_container_width=True, type="primary"):
            qr_base64 = generate_virtual_card_qr(card_id="WJ-35001-928", token="CANARIAS-OK")
            if qr_base64:
                st.markdown(f"""
                <div style="text-align: center; background: #ffffff; border-radius: 16px; border: 2px solid #002b49; padding: 18px; margin-top: 14px; box-shadow: 0 8px 20px rgba(0,43,73,0.1);">
                    <h4 style="margin: 0 0 6px 0; color: #002b49; font-weight: 800;">Acerca este código a la máquina canceladora</h4>
                    <p style="margin: 0 0 14px 0; font-size: 0.8rem; color: #64748b;">Válido durante 60 segundos por seguridad óptica</p>
                    <img src="{qr_base64}" style="width: 170px; height: 170px; border-radius: 10px; border: 1px solid #e2e8f0;"/>
                    <div style="margin-top: 10px; font-family: monospace; font-size: 0.85rem; color: #00778b; font-weight: bold;">
                        TOKEN: GLPA-CANARIAS-{int(datetime.now().timestamp()) % 10000}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("#### 🎯 Regla de los 15 Viajes (Gratuidad)")
        st.markdown("Simula tus viajes mensuales para comprobar si mantienes el transporte 100% subvencionado:")
        
        sim_trips = st.slider("Viajes realizados este mes:", min_value=0, max_value=35, value=12, step=1)
        sim_day = st.slider("Día actual del mes:", min_value=1, max_value=30, value=22, step=1)

        progress_info = calculate_free_transit_progress(sim_trips, sim_day)

        pct = progress_info["percentage"]
        st.progress(pct / 100.0)

        if progress_info["trips_remaining"] == 0:
            st.success(f"🎉 **¡Gratuidad Asegurada!** Has alcanzado {sim_trips} viajes (mínimo exigido: 15). Tu bono seguirá siendo 100% gratis el mes que viene.")
        else:
            st.warning(f"⏳ **Te faltan {progress_info['trips_remaining']} viajes** en los próximos {progress_info['days_left']} días para asegurar la gratuidad del próximo mes.")

        # Métricas de Ahorro en Euros
        single_ticket_cost = 2.45
        money_saved = sim_trips * single_ticket_cost
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Ahorro Acumulado este Mes", f"{money_saved:.2f} €", delta=f"{sim_trips} billetes gratis")
        col_m2.metric("Saldo en Monedero", "14,50 €", delta="Recarga automática")

        # Botonera de Recarga Rápida
        st.markdown("**⚡ Recarga Rápida de Saldo:**")
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        if col_r1.button("+5 €", use_container_width=True):
            st.toast("Recarga de 5€ procesada correctamente vía Bizum.")
        if col_r2.button("+10 €", use_container_width=True):
            st.toast("Recarga de 10€ procesada correctamente vía Apple/Google Pay.")
        if col_r3.button("+20 €", use_container_width=True):
            st.toast("Recarga de 20€ procesada correctamente.")
        if col_r4.button("+50 €", use_container_width=True):
            st.toast("Recarga de 50€ procesada correctamente.")

# ==============================================================================
# PESTAÑA 6: ⚠️ AVISOS DE SERVICIO (Incidencias en Vivo)
# ==============================================================================
with tab_alerts:
    st.markdown("### ⚠️ Avisos de Servicio e Incidencias en Red")
    st.markdown("Canal oficial de incidencias en directo sobre las autopistas de Gran Canaria y desvíos programados.")

    alerts = get_live_service_alerts()
    for al in alerts:
        st.markdown(f"""
        <div style="background: #ffffff; border-radius: 14px; border-left: 6px solid {'#ef4444' if al['type']=='warning' else ('#0284c7' if al['type']=='info' else '#10b981')}; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 800; font-size: 0.82rem; color: {'#b91c1c' if al['type']=='warning' else '#0369a1'};">
                    {al['icon']} {al['badge']}
                </span>
                <span style="font-size: 0.78rem; color: #64748b;">{al['timestamp']}</span>
            </div>
            <h4 style="margin: 0 0 6px 0; color: #002b49; font-size: 1.05rem; font-weight: 800;">{al['title']}</h4>
            <p style="margin: 0; color: #334155; font-size: 0.9rem;">{al['description']}</p>
            <div style="margin-top: 10px; display: flex; gap: 6px;">
                <span style="font-size: 0.75rem; color: #64748b; font-weight: 700;">Líneas afectadas:</span>
                {' '.join([f'<span style="background: #f1f5f9; color: #002b49; font-weight: 800; font-size: 0.75rem; padding: 2px 6px; border-radius: 4px;">{ln}</span>' for ln in al['affected_lines']])}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# PESTAÑA 7: 🔬 LABORATORIO & OPTIMIZACIÓN (Mini-TFG ULPGC)
# ==============================================================================
with tab_lab:
    st.markdown("### 🔬 Laboratorio de Optimización Insular (Temas 1, 2, 3 y 4)")
    st.markdown("Modelado matemático riguroso para la defensa académica del Mini-TFG (Grado en Ciencia e Ingeniería de Datos - ULPGC).")

    sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs([
        "Tema 1 & 3: MILP Flota (Simplex)",
        "Tema 2: Descenso Gradiente vs Newton",
        "Tema 3: Multiplicadores de Lagrange",
        "Tema 4: Algoritmos Genéticos vs SA",
    ])

    with sub_t1:
        st.markdown("#### Programación Lineal y Entera Mixta (MILP con Algoritmo Simplex)")
        st.latex(r"\max_{\mathbf{x}, \mathbf{s}} \sum_{i=1}^{5} \omega_i (d_i - s_i) \quad \text{s.t.} \quad \sum_{i=1}^{5} x_i \le B, \quad 65 x_i + s_i \ge d_i, \quad x_i \in \mathbb{Z}^+")
        
        milp_res = solve_fleet_dispatch_milp(total_available_buses=75)
        st.plotly_chart(plot_milp_dispatch_bars(milp_res.passengers_served, milp_res.passengers_unmet, milp_res.corridor_dispatches), use_container_width=True)

    with sub_t2:
        st.markdown("#### Optimización sin Restricciones: Calibración BPR (Gradiente vs Newton)")
        st.latex(r"\boldsymbol{\theta}^{(k+1)} = \boldsymbol{\theta}^{(k)} - \mathbf{H}(\boldsymbol{\theta}^{(k)})^{-1} \nabla f(\boldsymbol{\theta}^{(k)})")
        
        gd_res = optimize_bpr_gradient_descent(learning_rate=0.0005, max_iters=25)
        newton_res = optimize_bpr_newton(max_iters=10)
        st.plotly_chart(plot_unconstrained_convergence(gd_res.loss_history, newton_res.loss_history), use_container_width=True)

    with sub_t3:
        st.markdown("#### Optimización con Restricciones: Multiplicadores de Lagrange")
        st.latex(r"\mathcal{L}(f_1, \dots, f_K, \lambda) = \sum_{k=1}^K w_k \ln(f_k) - \lambda \left(\sum_{k=1}^K k_i f_i - B\right)")
        
        lagr_res = solve_lagrangian_frequency_allocation(total_budget_km=650.0)
        st.metric("Multiplicador Óptimo λ*", f"{lagr_res.lambda_multiplier:.4f}", delta="Coste sombra combustible / km")
        st.info(lagr_res.interpretation_lambda)
        st.dataframe(pd.DataFrame([{"Línea": k, "Frecuencia Óptima (exp/hora)": round(v, 2)} for k, v in lagr_res.optimal_frequencies.items()]), use_container_width=True)

    with sub_t4:
        st.markdown("#### Métodos Heurísticos: Simulated Annealing vs Algoritmo Genético")
        sa_res = solve_tsp_simulated_annealing(initial_temp=300.0, cooling_rate=0.97)
        ga_res = solve_tsp_genetic_algorithm(pop_size=50, generations=60)
        st.plotly_chart(plot_heuristic_convergence(sa_res.cost_history, ga_res.cost_history), use_container_width=True)
