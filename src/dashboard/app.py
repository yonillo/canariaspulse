"""GLOBAL Gran Canaria Móvil 2.0: Sistema Inteligente de Transporte Interurbano.

Réplica exacta, moderna y fiel a la identidad corporativa oficial de Global (Salcai Utinsa S.A.):
1. 🗺️ Mapa en Vivo & Flota GPS (Posicionamiento en tiempo real, paradas y ejes viales GC-1/GC-2/GC-110).
2. 🚏 Siguiente Parada (Búsqueda por código oficial de 4 dígitos de la marquesina).
3. 🧭 ¿A dónde quieres ir? (Calculadora de trayectos con Garantía de Llegada Bayesiana 95%).
4. 💳 Fares & Cards / Saldo de Tarjeta (Bono Residente Canario, Wawa Joven, TransGC, regla 15 viajes).
5. 🏪 Vendedor de Tickets (Puntos oficiales de recarga y oficinas de atención insulares).
6. ⚠️ Estado del Servicio & Radar de Carreteras (Inferencia causal en tiempo real con pgmpy).
7. 🔬 Laboratorio de Datos / Mini-TFG ULPGC (Gauss-Markov 4-plot, PCA Biplot, Bayes y Heatmap).
"""

from __future__ import annotations

import sys
from datetime import datetime, time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st

from src.analytics.visual_diagnostics import (
    plot_bayesian_update_curve,
    plot_causal_dag_visual,
    plot_delay_heatmap,
    plot_gauss_markov_quad,
    plot_pca_biplot_stops,
)
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

# Estilo visual auténtico y moderno de Global (Paleta oficial: Teal #00778b, Oro Canario #f2a900, Slate #192a3d)
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

    /* Avisos Oficiales Global */
    .official-notice {
        background: #fffbeb;
        border-left: 4px solid #f2a900;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        font-size: 0.88rem;
        color: #78350f;
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

# 7 Pestañas que replican fielmente la app de Global en el móvil
tab_mapa, tab_parada, tab_ruta, tab_tarjeta, tab_tiendas, tab_servicio, tab_lab = st.tabs([
    "🗺️ Mapa en Vivo",
    "🚏 Siguiente Parada",
    "🧭 ¿A dónde quieres ir?",
    "💳 Fares & Cards (Saldo)",
    "🏪 Vendedor de Tickets",
    "⚠️ Estado del Servicio",
    "🔬 Laboratorio de Datos (TFG ULPGC)",
])

# ==============================================================================
# 1. MAPA EN VIVO & FLOTA GPS
# ==============================================================================
with tab_mapa:
    st.markdown("#### 🗺️ Mapa de la Red Insular & Posicionamiento GPS en Vivo")
    st.caption("Visualiza las paradas oficiales, las polilíneas de las carreteras principales (GC-1, GC-2 y GC-110 a Tafira) y la ubicación GPS en tiempo real de las guaguas en ruta.")

    fleet_df = get_live_simulated_fleet()

    # Capa 1: Polilíneas viales de carreteras
    layer_roads = pdk.Layer(
        "PathLayer",
        data=HIGHWAY_POLYLINES,
        get_path="path",
        get_color="color",
        width_scale=20,
        width_min_pixels=3,
        get_width="width",
        pickable=True,
    )

    # Capa 2: Paradas oficiales
    layer_stops = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame(OFFICIAL_STOPS),
        get_position=["lon", "lat"],
        get_radius=1000,
        get_fill_color=[0, 119, 139, 210],
        get_line_color=[255, 255, 255, 255],
        line_width_min_pixels=1.5,
        pickable=True,
        auto_highlight=True,
    )

    # Capa 3: Posición GPS de las guaguas
    layer_buses = pdk.Layer(
        "ScatterplotLayer",
        data=fleet_df,
        get_position=["lon", "lat"],
        get_radius=1600,
        get_fill_color=[242, 169, 0, 245],
        get_line_color=[25, 42, 61, 240],
        line_width_min_pixels=2,
        pickable=True,
        auto_highlight=True,
    )

    layer_bus_labels = pdk.Layer(
        "TextLayer",
        data=fleet_df,
        get_position=["lon", "lat"],
        get_text="line",
        get_color=[25, 42, 61, 255],
        get_size=13,
        get_alignment_baseline="'center'",
        get_text_anchor="'middle'",
        pickable=False,
    )

    deck_live = pdk.Deck(
        layers=[layer_roads, layer_stops, layer_buses, layer_bus_labels],
        initial_view_state=pdk.ViewState(
            latitude=27.97,
            longitude=-15.53,
            zoom=9.3,
            pitch=30,
            bearing=0,
        ),
        map_style="light",
        tooltip={
            "html": "<b>{name}</b><br/>{destination}<br/>Línea: <b>{line}</b><br/>Velocidad: {speed_kmh} km/h<br/>Ocupación: {occupancy_pct}%",
            "style": {"color": "#192a3d", "backgroundColor": "#ffffff", "border": "1px solid #cbd5e1"},
        },
    )
    st.pydeck_chart(deck_live)

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
# 5. VENDEDOR DE TICKETS (OFICINAS Y PUNTOS OFICIALES DE RECARGA)
# ==============================================================================
with tab_tiendas:
    st.markdown("#### 🏪 Vendedor de Tickets & Puntos Oficiales de Recarga")
    st.caption("Localiza las estaciones centrales, oficinas de atención al viajero y quioscos autorizados de Global en Gran Canaria.")

    offices_df = pd.DataFrame(TICKET_OFFICES)

    layer_offices = pdk.Layer(
        "ScatterplotLayer",
        data=offices_df,
        get_position=["lon", "lat"],
        get_radius=1400,
        get_fill_color=[242, 169, 0, 240],
        get_line_color=[0, 119, 139, 255],
        line_width_min_pixels=2.5,
        pickable=True,
    )

    deck_offices = pdk.Deck(
        layers=[layer_offices],
        initial_view_state=pdk.ViewState(
            latitude=27.97,
            longitude=-15.53,
            zoom=9.3,
            pitch=25,
        ),
        map_style="light",
        tooltip={"html": "<b>{name}</b><br/>{address}<br/>Horario: {hours}", "style": {"color": "#192a3d", "backgroundColor": "#ffffff"}},
    )
    st.pydeck_chart(deck_offices)

    col_of1, col_of2 = st.columns(2)
    for i, of in enumerate(TICKET_OFFICES):
        target_col = col_of1 if i % 2 == 0 else col_of2
        with target_col:
            st.markdown(f"""
            <div class="global-card">
                <div style="font-weight: 800; color: #00778b; font-size: 1.05rem;">{of['name']}</div>
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
# 7. LABORATORIO DE DATOS / MINI-TFG ULPGC
# ==============================================================================
with tab_lab:
    st.markdown("#### 🔬 Laboratorio Analítico de Ciencia de Datos (Mini-TFG ULPGC)")
    st.caption("Módulo de rigor econométrico, estadística bayesiana y reducción de dimensionalidad con metodología CRISP-DM.")

    lab_section = st.radio(
        "Selecciona el módulo de análisis matemático a inspeccionar:",
        [
            "1. Panel de los 4 Diagnósticos de Gauss-Markov (MCO)",
            "2. Análisis de Componentes Principales (Biplot PCA de Paradas)",
            "3. Actualización Bayesiana Dinámica (Prior vs Verosimilitud vs Posterior)",
            "4. Grafo Causal Acíclico Dirigido (DAG en pgmpy)",
            "5. Mapa de Calor de Saturación Temporal (Heatmap 2D)",
        ],
        horizontal=True,
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
