# 🚌 GlobalPulse | Plataforma Analítica y Motor Estadístico de Movilidad (Gran Canaria)

> **Proyecto de Portfolio & CV** para el Grado en **Ciencia e Ingeniería de Datos** de la **Universidad de Las Palmas de Gran Canaria (ULPGC)**.

![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%20%7C%20Pydeck-FF4B4B.svg)
![Stats & ML](https://img.shields.io/badge/Stats-SciPy%20%7C%20Statsmodels%20%7C%20pgmpy-green.svg)
![Data](https://img.shields.io/badge/Data-OpenStreetMap%20%7C%20Global%20(Salcai%20Utinsa)-orange.svg)

---

## 📌 1. Visión del Proyecto y Problema Real

La movilidad en la isla de Gran Canaria representa uno de los mayores desafíos logísticos y de ingeniería del archipiélago:
* Atascos recurrentes en la arteria principal de la isla (**Autopista del Sur GC-1** y **GC-2**).
* Conexión crítica de transporte de pasajeros entre la capital (**Estación de San Telmo / Santa Catalina**), el **Aeropuerto de Gran Canaria (LPA)**, el **Campus Universitario de Tafira** y el polo turístico del sur (**Playa del Inglés, Maspalomas, Mogán**).
* Líneas de orografía compleja con desniveles de más de 800 metros en medianías y cumbres (**Línea 303 a San Mateo**).

**GlobalPulse** moderniza por completo la experiencia de usuario y la toma de decisiones:
1. **Cara al usuario / Móvil 2.0 ("El lavado de cara de Global")**: Una interfaz limpia, moderna y fiel a la identidad corporativa oficial de Global Salcai Utinsa (`#00778b` Teal, `#f2a900` Oro Canario, fondo blanco corporativo y tarjetas limpias). Integra las 6 funciones reales de la app móvil (Mapa GPS en vivo, Siguiente Parada por código de marquesina de 4 dígitos, ¿A dónde quieres ir? con Garantía de Llegada, Tarjetas & regla de 15 viajes de gratuidad en Canarias, Vendedor de tickets y Estado del Servicio).
2. **Bajo el capó (Motor Matemático & Laboratorio TFG ULPGC)**: Todo el sistema está impulsado por **inferencia estadística rigurosa, modelos de regresión MCO con diagnósticos de Gauss-Markov, mezclas gaussianas (GMM), biplot PCA 2D y redes bayesianas causales con inferencia exacta (pgmpy)**.

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

## 📂 3. Estructura del Repositorio

```text
global/
├── data/
│   ├── raw/                           # Paradas y topología extraídas de OpenStreetMap (Gran Canaria)
│   └── processed/                     # Telemetría operacional generada (Parquet y CSV)
├── src/
│   ├── data_ingestion/
│   │   └── extract_network.py         # Descarga de OSM, geocálculo ortodrómico (Haversine) y telemetría
│   ├── core_stats/
│   │   ├── distributions.py           # MLE, Poisson, Gamma, LogNormal, intervalos de confianza
│   │   ├── hypothesis_testing.py      # Welch t-test, Mann-Whitney, ANOVA, Levene, Chi-cuadrado
│   │   └── linear_regression.py       # OLS y diagnósticos completos de Gauss-Markov (VIF, BP, JB, DW)
│   ├── bayesian/
│   │   ├── conjugates.py              # Modelo conjugado Beta-Binomial y curvas de densidad
│   │   ├── bayesian_regression.py     # Regresión lineal bayesiana, incertidumbre epistémica y HDI 95%
│   │   ├── clustering_gmm.py          # Mezclas Gaussianas (GMM), EM y selección de k con BIC
│   │   └── bayesian_network.py        # Red Bayesiana causal insular y Variable Elimination con pgmpy
│   └── dashboard/
│       └── app.py                     # Aplicación web interactiva en Streamlit (El "Lavado de cara")
├── tests/
│   └── test_pipeline.py               # Suite de tests unitarios y validación matemática
├── requirements.txt                   # Dependencias fijadas del proyecto
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
```bash
streamlit run src/dashboard/app.py
```

La app se abrirá en tu navegador en `http://localhost:8501`, organizada en las 7 pestañas oficiales con estética corporativa de Global (Teal `#00778b`, Oro Canario `#f2a900`, tarjetas blancas y mapas viales en directo). En la pestaña **«🔬 Laboratorio de Datos (TFG ULPGC)»** puedes inspeccionar los diagnósticos de Gauss-Markov, el Biplot PCA 2D, las curvas bayesianas y el Grafo Causal DAG.
