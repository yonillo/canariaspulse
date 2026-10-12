# 🚌 CanariasPulse | Plataforma Analítica y Microapp Multimodal de Movilidad Canario-Insular

> **Proyecto de Portfolio & CV** para el Grado en **Ciencia e Ingeniería de Datos** de la **Universidad de Las Palmas de Gran Canaria (ULPGC)**.
> Red Unificada de Operadores: **Global (Gran Canaria)**, **TITSA (Tenerife)**, **Baleària**, **Fred. Olsen Express**, **Naviera Armas**, **Guaguas Municipales** y **Tranvía de Tenerife**.

![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)
![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%7C%20Tailwind%20%7C%20Leaflet-FF4B4B.svg)
![Stats & ML](https://img.shields.io/badge/Stats-SciPy%20%7C%20Statsmodels%20%7C%20pgmpy-green.svg)
![Coverage](https://img.shields.io/badge/Coverage-Gran%20Canaria%20%2B%20Tenerife%20%2B%20Mar%C3%ADtimo-orange.svg)

---

## 📌 1. Visión del Proyecto y Problema Real

La movilidad en el archipiélago canario representa uno de los mayores desafíos logísticos y de ingeniería del país:
* Atascos recurrentes en las dos arterias insulares principales (**Autopista del Sur GC-1 / GC-2 en Gran Canaria** y **TF-5 / TF-1 en Tenerife**).
* Fragmentación histórica de operadores: **Global** (interurbano GC), **TITSA** (interurbano Tenerife), **Guaguas Municipales** (Las Palmas), **Metrotenerife** (Tranvía), y navieras de conexión interinsular (**Baleària**, **Fred. Olsen Express**, **Naviera Armas**).
* Saturación masiva tras la gratuidad del transporte con el **Bono Residente Canario (regla de los 15 viajes mensuales)**.
* Desconexión entre los tiempos teóricos de llegada y la realidad del tráfico o mar de fondo en el canal interinsular.

**CanariasPulse** moderniza por completo la experiencia de usuario y la toma de decisiones:
1. **Cara al usuario / Microapp Unificada**: Interfaz ultraligera, responsiva y adaptable con mapa interactivo en tiempo real (Leaflet + OpenStreetMap), telemetría GPS multi-operador, planificador de viajes interinsulares, garantía de llegada bayesiana al 95% de confianza (HDI), y monitor del Bono Residente Canario de 15 viajes.
2. **Bajo el capó (Motor Matemático & Laboratorio TFG ULPGC)**: Impulsado por **inferencia estadística rigurosa, modelos de regresión MCO con diagnósticos de Gauss-Markov, mezclas gaussianas (GMM), biplot PCA 2D, optimización MILP con HiGHS y redes bayesianas causales con inferencia exacta (pgmpy)**.

---

## 🔬 2. Correspondencia Matemática con el Temario de Datos

El núcleo del proyecto (`src/core_stats/` y `src/bayesian/`) implementa directamente los fundamentos de la carrera:

### Bloque A: Fundamentos e Inferencia Estadística Clásica
* **Estadística Descriptiva y Distribuciones Continuas/Discretas (Temas 1, 3, 4)**:
  * Proceso de Poisson para modelar la afluencia de pasajeros por expedición: $X \sim \text{Poisson}(\lambda)$.
  * Modelado de tiempos de trayecto y retrasos mediante distribuciones **Log-Normal, Gamma y Weibull** (frente a la hipótesis simplista de normalidad).
* **Estimación Paramétrica por Máxima Verosimilitud (MLE) (Tema 7)**:
  * Ajuste analítico de parámetros y selección de modelos con los criterios de información **AIC** y **BIC**.
* **Intervalos de Confianza (Tema 8)**:
  * Intervalos al 95% para la media del tiempo de viaje con distribución $t$-Student e intervalos para la varianza mediante $\chi^2$.
* **Contrastes de Hipótesis y Tests de Significancia (Tema 9)**:
  * **Test de D'Agostino-Pearson**: Demostración formal de no normalidad en los tiempos de retraso.
  * **Welch's t-test y Mann-Whitney U**: Contraste de hipótesis sobre diferencias de puntualidad entre días laborables y fines de semana ($p < 0.001$).
  * **ANOVA de una vía y Kruskal-Wallis**: Contraste de igualdad de retrasos entre los tres grandes corredores de la isla (Corredor Sur, Corredor Norte y Medianías).
  * **Test Chi-cuadrado de independencia**: Demostración de asociación entre hora punta y estado de retraso.
* **Modelo de Regresión Lineal y Diagnósticos de Gauss-Markov (Tema 10)**:
  * Modelo explicativo: $\text{Tiempo} = \beta_0 + \beta_1 \cdot \text{Distancia} + \beta_2 \cdot \text{Desnivel} + \beta_3 \cdot \text{HoraPunta} + \beta_4 \cdot \text{FinSemana} + \beta_5 \cdot \text{IncidenteGC1} + \epsilon$.
  * Verificación de supuestos:
    * Test de **Breusch-Pagan** (diagnóstico de heterocedasticidad).
    * Test de **Jarque-Bera** (normalidad de residuos).
    * Factores de Inflación de la Varianza (**VIF**) para descartar multicolinealidad severa.
    * Estadístico de **Durbin-Watson** para independencia de errores.

---

### Bloque B: Inferencia Bayesiana y Machine Learning Probabilístico
* **Estimación Bayesiana Exacta (Familias Conjugadas - Tema 2)**:
  * Modelo **Beta-Binomial** para estimar la tasa real de puntualidad $\theta$ de cada línea:
    $$\theta \mid D \sim \text{Beta}(\alpha_0 + \text{éxitos}, \, \beta_0 + \text{fracasos})$$
  * Actualización secuencial diaria y cálculo del **Highest Density Interval (HDI)** al 95%.
* **Regresión Lineal Bayesiana con Distribución Predictiva a Posteriori (Temas 3 y 4)**:
  * Distribución a priori Gaussiana en los pesos: $\beta \sim \mathcal{N}(\mu_0, \Sigma_0)$.
  * Distribución predictiva analítica para un nuevo trayecto:
    $$p(y_* \mid x_*, \mathcal{D}) \sim \mathcal{N}\left(x_* \mu_N, \, \sigma_{\text{aleatorio}}^2 + x_* \Sigma_N x_*^T\right)$$
  * Muestreo de Monte Carlo para devolver al usuario no una sola cifra, sino un **intervalo de credibilidad al 95%** junto con un índice semántico de certidumbre.
* **Clustering Probabilístico con Modelos de Mezclas Gaussianas (GMM - Tema 5)**:
  * Segmentación no supervisada de las paradas y estaciones insulares mediante el algoritmo **Esperanza-Maximización (EM)**.
  * Cálculo de responsabilidades a posteriori:
    $$\gamma_{ik} = P(\text{Cluster} = k \mid x_i)$$
  * Clasificación automática de paradas: *Hubs e Intercambiadores*, *Polos Universitarios*, *Corredor Turístico de Playa* y *Medianías*.
* **Redes Bayesianas e Inferencia Causal (pgmpy - Tema 6)**:
  * Modelado de la red de carreteras con un **Grafo Acíclico Dirigido (DAG)** que captura dependencias condicionales reales:
    $$\text{Incidente GC-1} \rightarrow \text{Colapso Hoya de la Plata} \rightarrow \text{Retraso L30 Sur} \rightarrow \text{Pérdida Vuelo Aeropuerto}$$
  * Motor de inferencia exacta mediante el algoritmo de **Eliminación de Variables (Variable Elimination)** para calcular en tiempo real el efecto dominó de cualquier avería o alerta climática.

---

### Bloque C: Métodos de Optimización Matemática (Temas 1, 2, 3 y 4 del Grado)
* **Programación Lineal y Entera Mixta (MILP / Método Simplex - Temas 1 y 3)**:
  * Despacho óptimo de flota de 412 guaguas y horas de conductor en horas punta insulares mediante `scipy.optimize.milp` (HiGHS) con precios sombra duales.
* **Optimización Sin Restricciones (Descenso por Gradiente vs Newton - Tema 2)**:
  * Calibración de la función de coste vial BPR calculando analíticamente el gradiente $\nabla f$ y la matriz Hessiana $\mathbf{H}$, contrastando convergencia lineal frente a cuadrática.
* **Multiplicadores de Lagrange (Tema 3.2)**:
  * Asignación óptima de frecuencias de servicio bajo restricción presupuestaria de kilómetros, con interpretación económica del multiplicador $\lambda^*$ (utilidad marginal).
* **Metaheurísticas: Simulated Annealing y Algoritmos Genéticos (Tema 4)**:
  * Enrutamiento óptimo de circuitos de refuerzo e inspección (TSP sobre paradas insulares clave) con operadores 2-opt y cruce Order Crossover (OX).

---

## 📂 3. Estructura del Repositorio

```text
global/
├── data/
│   ├── raw/                           # Paradas y topología extraídas de OpenStreetMap (Gran Canaria)
│   └── processed/                     # Telemetría operacional generada (Parquet y CSV)
├── src/
│   ├── data_ingestion/
│   │   ├── extract_network.py         # Descarga de OSM, geocálculo ortodrómico (Haversine) y telemetría
│   │   └── network_data.py            # Trazados viales, paradas oficiales y telemetría GPS en directo
│   ├── core_stats/
│   │   ├── distributions.py           # MLE, Poisson, Gamma, LogNormal, intervalos de confianza
│   │   ├── hypothesis_testing.py      # Welch t-test, Mann-Whitney, ANOVA, Levene, Chi-cuadrado
│   │   └── linear_regression.py       # OLS y diagnósticos completos de Gauss-Markov (VIF, BP, JB, DW)
│   ├── bayesian/
│   │   ├── conjugates.py              # Modelo conjugado Beta-Binomial y curvas de densidad
│   │   ├── bayesian_regression.py     # Regresión lineal bayesiana, incertidumbre epistémica y HDI 95%
│   │   ├── clustering_gmm.py          # Mezclas Gaussianas (GMM), EM y selección de k con BIC
│   │   └── bayesian_network.py        # Red Bayesiana causal insular y Variable Elimination con pgmpy
│   ├── optimization/
│   │   ├── fleet_dispatch_milp.py     # Programación Lineal y Entera Mixta (HiGHS / Simplex)
│   │   ├── unconstrained_gradient.py  # Descenso por Gradiente y Método de Newton con Hessiano
│   │   ├── lagrangian_allocation.py   # Multiplicadores de Lagrange y coste sombra
│   │   └── heuristic_routing.py       # Simulated Annealing y Algoritmo Genético (TSP insular)
│   ├── analytics/
│   │   └── visual_diagnostics.py      # Gauss-Markov 4-plot, Biplot PCA 2D, Bayes, Heatmap y Optimización
│   └── dashboard/
│       └── app.py                     # Global Móvil 2.0 (Google Maps + 7 Pestañas Oficiales)
├── tests/
│   ├── test_mathematical_properties.py # Tests unitarios de inferencia estadística y bayesiana
│   ├── test_optimization.py           # Tests unitarios de MILP, Newton, Lagrange y Heurísticas
│   └── test_pipeline.py               # Test de integración del pipeline completo
├── requirements.txt                   # Dependencias fijadas del proyecto (incluye folium y streamlit-folium)
└── README.md                          # Documentación técnica del proyecto
```


---

## 🚀 4. Instalación y Ejecución

### 1. Clonar e Instalar Dependencias
```bash
cd C:\Users\elyon\Desktop\global
pip install -r requirements.txt
```

### 2. Ejecutar la Batería de Pruebas Matemáticas
Para verificar que todos los contrastes de hipótesis, modelos MCO y redes bayesianas pasan:
```bash
python -m pytest tests/
```

### 3. Lanzar la Aplicación Interactiva

Dispones de dos modalidades de interfaz según el caso de uso:

#### Opción A: Frontend Moderno de Alta Fidelidad (Recomendado - 60 FPS Citymapper / Apple Maps Feel)
Ejecuta el servidor unificado FastAPI que sirve directamente la aplicación **React 19 + Tailwind CSS + Leaflet** con mapa interactivo a pantalla completa, drawer lateral flotante y microinteracciones:
```bash
python run_app.py
```
Se abrirá automáticamente en tu navegador en **`http://localhost:8000`** (con documentación interactiva Swagger API en `http://localhost:8000/docs`).

Para desarrollo activo del frontend con Hot-Reload:
```bash
cd frontend
npm run dev
```
(Acceso en `http://localhost:3000`).

---

#### Opción B: Cuadro de Mandos en Streamlit
Si prefieres ejecutar el prototipo clásico en Streamlit:
```bash
streamlit run src/dashboard/app.py
```
(Acceso en `http://localhost:8501`).
