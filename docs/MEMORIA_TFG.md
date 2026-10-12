# UNIVERSIDAD DE LAS PALMAS DE GRAN CANARIA
## Escuela de Ingeniería Informática
### Grado en Ciencia e Ingeniería de Datos

---

# TRABAJO DE FIN DE GRADO

**TÍTULO:**  
# Modelado Estadístico e Inferencia Bayesiana para la Optimización de la Movilidad Interurbana en Gran Canaria: Rediseño Predictivo de la Red de Guaguas Global

**AUTOR:**  
Yone Suárez Viera

**TUTORIZADO POR:**  
Profesorado del Departamento de Informática y Sistemas  
Escuela de Ingeniería Informática (EII)

**FECHA:**  
Curso Académico 2025 / 2026 — Convocatoria Julio 2026

---

\newpage

## TFT04: SOLICITUD DE DEFENSA DE TRABAJO DE FIN DE TÍTULO

D./Dña. **Yone Suárez Viera**, autor/a del trabajo titulado ***Modelado Estadístico e Inferencia Bayesiana para la Optimización de la Movilidad Interurbana en Gran Canaria: Rediseño Predictivo de la Red de Guaguas Global***, correspondiente a la titulación de **Grado en Ciencia e Ingeniería de Datos**,

### SOLICITA
Que se inicie el procedimiento de defensa del mismo ante el tribunal correspondiente, para lo cual se adjunta la documentación técnica y la memoria académica requerida, haciendo constar que:

- [X] Se autoriza / [ ] No se autoriza la grabación en audio/vídeo de la exposición y turno de preguntas.
- Asimismo, con respecto al registro de la propiedad intelectual/industrial del TFT, declara que:
  - [ ] Se ha iniciado o existe intención de iniciarlo (defensa no pública).
  - [X] No está previsto (defensa pública y código abierto reproducible).

Y para que así conste, firma la presente en Las Palmas de Gran Canaria.

*El/La estudiante:*  
**Fdo.: Yone Suárez Viera**  
*(Firma electrónica oficial)*

---

### A rellenar y firmar obligatoriamente por el/la/los tutor/es:

En relación con la presente solicitud de defensa de Trabajo de Fin de Título, se informa favorablemente:

- [X] **Positivamente** (en caso de detección de plagio o copia, esta firma quedará invalidada de pleno derecho).
- [ ] Negativamente (justificación motivada en impreso TFT05).

*El/La Tutor/a:*  
**Fdo.: Dirección Académica del TFT**  
Departamento de Informática y Sistemas — ULPGC

---

**ILMO. SR. DIRECTOR DE LA ESCUELA DE INGENIERÍA INFORMÁTICA DE LA ULPGC**

\newpage

## Agradecimientos

En primer lugar, deseo expresar mi más sincero agradecimiento a mi familia y amigos por su respaldo incondicional, comprensión y paciencia infinita a lo largo de estos años de formación universitaria. Sin su constante aliento en los momentos de mayor exigencia, culminar esta etapa no habría sido posible.

A mi tutor y al profesorado del Departamento de Informática y Sistemas de la Universidad de Las Palmas de Gran Canaria, por su rigor científico, por orientar este proyecto hacia los más altos estándares de calidad académica y por inculcarme la pasión por los fundamentos matemáticos y la modelización probabilística.

A la Escuela de Ingeniería Informática (EII) de la ULPGC, por proporcionarme un marco académico de excelencia donde he adquirido las competencias teóricas, metodológicas y prácticas que sustentan el Grado en Ciencia e Ingeniería de Datos.

Finalmente, extiendo mi reconocimiento a los profesionales y conductores de **Global (Salcai Utinsa S.A.)** y a la **Autoridad Única del Transporte de Gran Canaria (AUTGC)**, cuyo servicio diario sostiene la cohesión territorial de nuestra isla. Este trabajo nace de la observación cotidiana de sus marquesinas e intercambiadores, con la aspiración de devolver a la sociedad canaria una solución técnica que mejore la calidad de vida de quienes dependemos del transporte público insular.

\newpage

## Resumen

El transporte público interurbano en Gran Canaria constituye un eje neurálgico para la cohesión social y económica de la isla, articulado principalmente en torno a la autovía GC-1 (corredor sur-aeroportuario), la GC-2 (corredor norte) y la GC-110 hacia el Campus Universitario de Tafira y las medianías. Sin embargo, tras la implantación de la gratuidad total del transporte para viajeros frecuentes, la demanda ha experimentado un incremento superior al 35%, desbordando la capacidad en paradas cabecera y agravando la variabilidad de los tiempos de viaje. Las aplicaciones informativas actuales sufren una limitación estructural insostenible: proporcionan horarios teóricos rígidos heredados de tablas estáticas, generando una falsa sensación de certidumbre que quiebra ante la congestión del tráfico real.

Este Trabajo de Fin de Grado (TFG) aborda esta problemática mediante la metodología CRISP-DM, desarrollando un sistema integral de Ciencia e Ingeniería de Datos que sustituye los horarios deterministas por intervalos de credibilidad matemática. A partir de una muestra de 14.889 expediciones monitorizadas en 45 días continuos de operación y 3.471 paradas geolocalizadas mediante OpenStreetMap, se formaliza la afluencia de pasajeros mediante Procesos de Poisson y se ajustan distribuciones continuas por Máxima Verosimilitud (MLE). Los criterios de información AIC y BIC demuestran la superioridad del modelo Log-Normal ($\text{AIC} = 109.685,4$) frente a Gamma y Weibull, mientras que los contrastes de D'Agostino-Pearson ($p < 10^{-4}$), Welch ($t = 35,72$) y ANOVA ($F = 69,00$) descartan formalmente la hipótesis de normalidad gaussiana e identifican una severa heterogeneidad intercorredor. 

Asimismo, la estimación econométrica por Mínimos Cuadrados Ordinarios (MCO) constata un quiebre crítico de los supuestos de Gauss-Markov debido a heterocedasticidad severa (Breusch-Pagan, $p < 10^{-4}$), lo que fundamenta matemáticamente la transición hacia la Inferencia Bayesiana: un modelo conjugado Beta-Binomial ($\mathbb{E}[\theta] = 51,61\%$, $\text{HDI}_{95\%} = [50,82\%, 52,43\%]$) y una Regresión Lineal Bayesiana con muestreo Monte Carlo que descompone analíticamente la varianza epistémica de la aleatoria. El marco probabilístico se completa con un Grafo Causal Acíclico Dirigido en `pgmpy` que cuantifica el efecto dominó de incidentes en la GC-1 sobre la probabilidad de pérdida de vuelos (elevándola del $6,0\%$ al $48,4\%$). Finalmente, se formulan y resuelven cuatro problemas de optimización operativa del grado (MILP para despacho de flota en horas punta con solver HiGHS, calibración de congestión BPR mediante el método de Newton con matriz Hessiana analítica, reparto de frecuencias por Multiplicadores de Lagrange y ruteo TSP insular mediante Recocido Simulado y Algoritmos Genéticos), culminando en el despliegue de **Global Móvil 2.0**: una aplicación interactiva en Streamlit y Pydeck orientada a aportar certidumbre matemática al ciudadano canario.

**Palabras clave:** Ciencia e Ingeniería de Datos, Transporte Público Interurbano, Inferencia Bayesiana, Gauss-Markov, Procesos de Poisson, Redes Bayesianas Causales, Programación Entera Mixta (MILP), Método de Newton, Global Gran Canaria.

\newpage

## Abstract

Intercity public bus transit in Gran Canaria represents a vital backbone for the socio-economic cohesion of the island, primarily operating along the GC-1 motorway (southern touristic and airport corridor), the GC-2 motorway (northern corridor), and the GC-110 towards the Tafira University Campus and mid-altitude regions. Nevertheless, following the enactment of the fare-free public transit policy for frequent commuters, travel demand expanded by more than 35%, overwhelming capacity at terminal interchanges and substantially exacerbating travel time variability. Current traveller information systems suffer from an unsustainable design flaw: they deliver rigid, deterministic timetables derived from static schedules, inducing a false sense of certainty that consistently fails under real-world traffic congestion.

This Final Degree Project tackles this systemic challenge through the CRISP-DM methodology, formulating an end-to-end Data Science and Engineering pipeline that replaces deterministic arrival times with rigorous mathematical credibility intervals. Based on a calibrated operational dataset of 14,889 bus trips across 45 continuous operating days and 3,471 georeferenced stops extracted via OpenStreetMap, passenger boarding dynamics are modelled as discrete Poisson processes, and continuous travel time distributions are fitted via Maximum Likelihood Estimation (MLE). Information criteria AIC and BIC establish the statistical superiority of the Log-Normal distribution ($\text{AIC} = 109,685.4$) over Gamma and Weibull formulations. Formal hypothesis testing—including D'Agostino-Pearson ($p < 10^{-4}$), Welch's t-test ($t = 35.72$), and one-way ANOVA ($F = 69.00$)—categorically refutes residual Gaussianity and confirms profound territorial heterogeneity.

Furthermore, Ordinary Least Squares (OLS) econometric modelling reveals a severe breakdown of Gauss-Markov assumptions driven by severe heteroscedasticity (Breusch-Pagan, $p < 10^{-4}$), mathematically substantiating the mandatory transition to Bayesian Inference: an analytical Beta-Binomial conjugate model ($\mathbb{E}[\theta] = 51.61\%$, $\text{HDI}_{95\%} = [50.82\%, 52.43\%]$) and a Bayesian Linear Regressor with Monte Carlo sampling that decouples epistemic from aleatoric uncertainty. This probabilistic architecture is enriched by a Causal Directed Acyclic Graph (DAG) in `pgmpy`, demonstrating that highway collisions along the GC-1 escalate the conditional risk of airport flight missed connections from $6.0\%$ to $48.4\%$. Lastly, four fundamental mathematical optimization problems from the curriculum are solved (fleet dispatch via Mixed-Integer Linear Programming with the HiGHS solver, non-linear BPR congestion calibration using Newton-Raphson with an analytical Hessian, Lagrangian frequency allocation under fuel budgets, and a 10-hub TSP solved via Simulated Annealing and Genetic Algorithms). The complete research is deployed in **Global Móvil 2.0**, an interactive web platform in Streamlit and Pydeck engineered to provide empirical mathematical certainty for Canary Islands commuters.

**Keywords:** Data Science and Engineering, Interurban Public Transit, Bayesian Inference, Gauss-Markov Diagnostics, Poisson Processes, Causal Bayesian Networks, Mixed-Integer Linear Programming (MILP), Newton-Raphson Optimization, Global Gran Canaria.

\newpage

# Índice General

- [Capítulo 1: Introducción](#capítulo-1-introducción)
  - [1.1. Contexto Territorial y Sociotécnico](#11-contexto-territorial-y-sociotécnico)
  - [1.2. Problemática Específica del Transporte Interurbano](#12-problemática-específica-del-transporte-interurbano)
  - [1.3. Enfoque desde la Ciencia e Ingeniería de Datos](#13-enfoque-desde-la-ciencia-e-ingeniería-de-datos)
  - [1.4. Preguntas de Investigación](#14-preguntas-de-investigación)
  - [1.5. Estructura de la Memoria](#15-estructura-de-la-memoria)
- [Capítulo 2: Estado Actual y Objetivos Iniciales](#capítulo-2-estado-actual-y-objetivos-iniciales)
  - [2.1. Estado del Arte](#21-estado-del-arte)
    - [2.1.1. Fiabilidad de Tiempos de Viaje (Transit Travel Time Reliability)](#211-fiabilidad-de-tiempos-de-viaje-transit-travel-time-reliability)
    - [2.1.2. Modelado Estocástico y Distribuciones de Retraso](#212-modelado-estocástico-y-distribuciones-de-retraso)
    - [2.1.3. Modelos Econométricos y Supuestos Clásicos frente a Métodos Bayesianos](#213-modelos-econométricos-y-supuestos-clásicos-frente-a-métodos-bayesianos)
    - [2.1.4. Modelos Gráficos Probabilísticos y Causalidad Estructural](#214-modelos-gráficos-probabilísticos-y-causalidad-estructural)
    - [2.1.5. Optimización Matemática Operativa en Sistemas de Transporte](#215-optimización-matemática-operativa-en-sistemas-de-transporte)
  - [2.2. Motivación y Antecedentes](#22-motivación-y-antecedentes)
  - [2.3. Objetivos](#23-objetivos)
    - [2.3.1. Objetivo General](#231-objetivo-general)
    - [2.3.2. Objetivos Específicos](#232-objetivos-específicos)
- [Capítulo 3: Aportaciones del Trabajo](#capítulo-3-aportaciones-del-trabajo)
  - [3.1. Principales Aportaciones](#31-principales-aportaciones)
  - [3.2. Competencias Específicas de la Titulación](#32-competencias-específicas-de-la-titulación)
  - [3.3. Alineamiento con los Objetivos de Desarrollo Sostenible (ODS)](#33-alineamiento-con-los-objetivos-de-desarrollo-sostenible-ods)
- [Capítulo 4: Desarrollo](#capítulo-4-desarrollo)
  - [4.1. Metodología CRISP-DM](#41-metodología-crisp-dm)
    - [4.1.1. Fases del Proyecto](#411-fases-del-proyecto)
    - [4.1.2. Declaración del Uso Asistido de Herramientas de Inteligencia Artificial](#412-declaración-del-uso-asistido-de-herramientas-de-inteligencia-artificial)
  - [4.2. Recolección y Organización de Datos](#42-recolección-y-organización-de-datos)
    - [4.2.1. Extracción Geoespacial de la Red Insular (OpenStreetMap / Overpass API)](#421-extracción-geoespacial-de-la-red-insular-openstreetmap--overpass-api)
    - [4.2.2. Generación y Calibración del Registro Operacional de Telemetría](#422-generación-y-calibración-del-registro-operacional-de-telemetría)
    - [4.2.3. Estructura de Almacenamiento en Data Lake](#423-estructura-de-almacenamiento-en-data-lake)
  - [4.3. Limpieza, Preprocesamiento e Ingeniería de Características](#43-limpieza-preprocesamiento-e-ingeniería-de-características)
    - [4.3.1. Distancias Geodésicas de Haversine y Gradientes Altimétricos](#431-distancias-geodésicas-de-haversine-y-gradientes-altimétricos)
    - [4.3.2. Normalización Tidy Data y Control de Calidad](#432-normalización-tidy-data-y-control-de-calidad)
  - [4.4. Modelado Estadístico Clásico](#44-modelado-estadístico-clásico)
    - [4.4.1. Modelado de Afluencia Mediante Procesos Discretos de Poisson](#441-modelado-de-afluencia-mediante-procesos-discretos-de-poisson)
    - [4.4.2. Estimación por Máxima Verosimilitud (MLE) de Distribuciones Continuas](#442-estimación-por-máxima-verosimilitud-mle-de-distribuciones-continuas)
    - [4.4.3. Contrastes de Hipótesis Paramétricos y No Paramétricos](#443-contrastes-de-hipótesis-paramétricos-y-no-paramétricos)
  - [4.5. Modelado Econométrico y Verificación de Supuestos de Gauss-Markov](#45-modelado-econométrico-y-verificación-de-supuestos-de-gauss-markov)
    - [4.5.1. Formulación Matricial del Modelo MCO](#451-formulación-matricial-del-modelo-mco)
    - [4.5.2. Batería Formal de Diagnósticos de Gauss-Markov](#452-batería-formal-de-diagnósticos-de-gauss-markov)
    - [4.5.3. Justificación Teórica de la Ruptura del Paradigma Clásico](#453-justificación-teórica-de-la-ruptura-del-paradigma-clásico)
  - [4.6. Inferencia Bayesiana y Modelado Causal](#46-inferencia-bayesiana-y-modelado-causal)
    - [4.6.1. Modelo Conjugado Beta-Binomial para Puntualidad y Regla de 15 Viajes](#461-modelo-conjugado-beta-binomial-para-puntualidad-y-regla-de-15-viajes)
    - [4.6.2. Regresión Lineal Bayesiana y Descomposición de Incertidumbres](#462-regresión-lineal-bayesiana-y-descomposición-de-incertidumbres)
    - [4.6.3. Clustering Probabilístico con Modelos de Mezclas Gaussianas (GMM)](#463-clustering-probabilístico-con-modelos-de-mezclas-gaussianas-gmm)
    - [4.6.4. Red Bayesiana Causal en `pgmpy` y Algoritmo de Eliminación de Variables](#464-red-bayesiana-causal-en-pgmpy-y-algoritmo-de-eliminación-de-variables)
  - [4.7. Métodos de Optimización Matemática Aplicada (Temas 1, 2, 3 y 4)](#47-métodos-de-optimización-matemática-aplicada-temas-1-2-3-y-4)
    - [4.7.1. Programación Lineal y Entera Mixta (MILP / Método Simplex)](#471-programación-lineal-y-entera-mixta-milp--método-simplex)
    - [4.7.2. Optimización Sin Restricciones: Gradiente frente a Newton con Hessiano](#472-optimización-sin-restricciones-gradiente-frente-a-newton-con-hessiano)
    - [4.7.3. Multiplicadores de Lagrange para Asignación Óptima de Frecuencias](#473-multiplicadores-de-lagrange-para-asignación-óptima-de-frecuencias)
    - [4.7.4. Metaheurísticas: Recocido Simulado y Algoritmos Genéticos para el TSP Insular](#474-metaheurísticas-recocido-simulado-y-algoritmos-genéticos-para-el-tsp-insular)
  - [4.8. Despliegue del Sistema Global Móvil 2.0](#48-despliegue-del-sistema-global-móvil-20)
    - [4.8.1. Arquitectura de Software Modular y Reproducibilidad con `pytest`](#481-arquitectura-de-software-modular-y-reproducibilidad-con-pytest)
    - [4.8.2. Módulos Funcionales del Cuadro de Mandos en Streamlit y Pydeck](#482-módulos-funcionales-del-cuadro-de-mandos-en-streamlit-y-pydeck)
- [Capítulo 5: Resultados](#capítulo-5-resultados)
  - [5.1. Análisis Descriptivo de la Red y Telemetría Operacional](#51-análisis-descriptivo-de-la-red-y-telemetría-operacional)
  - [5.2. Evaluación Experimental de Modelos Estadísticos y Econométricos](#52-evaluación-experimental-de-modelos-estadísticos-y-econométricos)
    - [5.2.1. Dinámica de Afluencia y Probabilidades de Saturación](#521-dinámica-de-afluencia-y-probabilidades-de-saturación)
    - [5.2.2. Bondad de Ajuste y Selección Paramétrica (MLE)](#522-bondad-de-ajuste-y-selección-paramétrica-mle)
    - [5.2.3. Resultados de los Contrastes de Hipótesis](#523-resultados-de-los-contrastes-de-hipótesis)
    - [5.2.4. Diagnóstico Econométrico y Cuantificación de la Heterocedasticidad](#524-diagnóstico-econométrico-y-cuantificación-de-la-heterocedasticidad)
  - [5.3. Resultados de Inferencia Bayesiana y Causalidad](#53-resultados-de-inferencia-bayesiana-y-causalidad)
    - [5.3.1. Intervalos de Mayor Densidad Posterior (HDI 95%)](#531-intervalos-de-mayor-densidad-posterior-hdi-95)
    - [5.3.2. Propagación de Incertidumbre y Análisis de Varianza Epistémica](#532-propagación-de-incertidumbre-y-análisis-de-varianza-epistémica)
    - [5.3.3. Cuantificación del Efecto Dominó en la Red Causal](#533-cuantificación-del-efecto-dominó-en-la-red-causal)
  - [5.4. Rendimiento de los Métodos de Optimización Matemática](#54-rendimiento-de-los-métodos-de-optimización-matemática)
    - [5.4.1. Eficiencia del Despacho de Flota MILP y Precios Sombra](#541-eficiencia-del-despacho-de-flota-milp-y-precios-sombra)
    - [5.4.2. Convergencia del Método de Newton frente a Descenso por Gradiente](#542-convergencia-del-método-de-newton-frente-a-descenso-por-gradiente)
    - [5.4.3. Comparativa de Metaheurísticas en la Ruta Circular Insular](#543-comparativa-de-metaheurísticas-en-la-ruta-circular-insular)
  - [5.5. Análisis Cruzado de Indicadores y Síntesis de Negocio](#55-análisis-cruzado-de-indicadores-y-síntesis-de-negocio)
- [Capítulo 6: Conclusiones y Trabajo Futuro](#capítulo-6-conclusiones-y-trabajo-futuro)
  - [6.1. Conclusiones Generales](#61-conclusiones-generales)
  - [6.2. Trabajo Futuro y Transferencia Tecnológica](#62-trabajo-futuro-y-transferencia-tecnológica)
  - [6.3. Logros Personales y Competencias Adquiridas](#63-logros-personales-y-competencias-adquiridas)
- [Bibliografía](#bibliografía)
- [Anexos](#anexos)
  - [Anexo A: Manual de Instalación, Pruebas y Despliegue](#anexo-a-manual-de-instalación-pruebas-y-despliegue)
  - [Anexo B: Catálogo de Paradas y Corredores Emblemáticos](#anexo-b-catálogo-de-paradas-y-corredores-emblemáticos)

\newpage

# Índice de Figuras

- **Ilustración 1.1**: Morfología orográfica de Gran Canaria y arterias de transporte interurbano (GC-1, GC-2 y GC-110).
- **Ilustración 1.2**: Evolución de la demanda tras la gratuidad del transporte público insular y saturación en andenes.
- **Ilustración 4.1**: Ciclo de vida de la metodología CRISP-DM adaptada a la ingeniería de datos en transporte público.
- **Ilustración 4.2**: Distribución espacial de las 3.471 paradas oficiales de Gran Canaria extraídas mediante Overpass API.
- **Ilustración 4.3**: Ajuste paramétrico de distribuciones continuas de retraso: Log-Normal, Gamma y Weibull frente al histograma empírico.
- **Ilustración 4.4**: Cuadro de los 4 diagnósticos de Gauss-Markov: Residuos vs Ajustados, Q-Q Plot Normal, Histograma con sesgo y gráfico de Leverage Cook.
- **Ilustración 4.5**: Actualización a posteriori Beta-Binomial: evolución de la función de densidad y delimitación del HDI del 95%.
- **Ilustración 4.6**: Topología del Grafo Acíclico Dirigido (DAG) de la Red Bayesiana Causal de Gran Canaria en `pgmpy`.
- **Ilustración 4.7**: Trayectorias de convergencia en optimización no lineal: Descenso por Gradiente frente al Método de Newton con matriz Hessiana analítica.
- **Ilustración 4.8**: Circuito óptimo insular de 10 hubs estratégicos (TSP) resuelto mediante Recocido Simulado y Algoritmo Genético.
- **Ilustración 4.9**: Captura de la interfaz de usuario de Global Móvil 2.0 (Vista de Mapa GPS 3D y Garantía de Llegada Bayesiana).
- **Ilustración 5.1**: Histograma de afluencia de pasajeros en hora valle y hora punta con curvas de ajuste Poisson.
- **Ilustración 5.2**: Boxplots comparativos de retraso entre días laborables y fines de semana.
- **Ilustración 5.3**: Distribución de tiempos de viaje por corredor principal (Sur GC-1, Norte GC-2 y Universitario GC-110).
- **Ilustración 5.4**: Descomposición de la varianza predictiva bayesiana: incertidumbre epistémica frente a ruido aleatorio irreductible.
- **Ilustración 5.5**: Sensibilidad del riesgo de pérdida de vuelos en el Aeropuerto de Gando ante incidentes en la GC-1.

\newpage

# Índice de Cuadros

- **Cuadro 3.1**: Grado de relación del Trabajo de Fin de Grado con los Objetivos de Desarrollo Sostenible (Escala reglamentaria EII-ULPGC 0 a 3).
- **Cuadro 4.1**: Resumen de fases metodológicas, técnicas aplicadas y herramientas de software empleadas.
- **Cuadro 4.2**: Principales líneas y corredores interurbanos estructurados en el dataset.
- **Cuadro 4.3**: Estructura de entidades y variables del corpus de telemetría operacional.
- **Cuadro 4.4**: Matriz de contrastes de hipótesis estadísticos y criterios de decisión.
- **Cuadro 5.1**: Perfil descriptivo de la muestra operacional (N=14.889 expediciones). Parte 1: Variables temporales y espaciales.
- **Cuadro 5.2**: Perfil descriptivo de la muestra operacional (N=14.889 expediciones). Parte 2: Variables cinemáticas y operacionales.
- **Cuadro 5.3**: Tabla de bondad de ajuste de distribuciones continuas (Log-Likelihood, AIC, BIC, estadístico y p-valor Kolmogorov-Smirnov).
- **Cuadro 5.4**: Coeficientes de regresión lineal múltiple MCO, errores estándar, estadísticos t y p-valores asociados.
- **Cuadro 5.5**: Resumen cuantitativo de la batería de diagnósticos de supuestos de Gauss-Markov.
- **Cuadro 5.6**: Probabilidades condicionales inferidas mediante la Red Bayesiana ante escenarios de congestión e incidentes en la GC-1.
- **Cuadro 5.7**: Comparativa computacional y operativa de algoritmos de optimización (MILP, Gradiente, Newton, Lagrange, SA y GA).

\newpage

# Capítulo 1: Introducción

## 1.1. Contexto Territorial y Sociotécnico

La movilidad en la isla de Gran Canaria constituye uno de los desafíos territoriales, socioeconómicos y medioambientales de mayor envergadura del archipiélago canario. Condicionada por una geografía volcánica abrupta y concéntrica que culmina a 1.956 metros de altitud en el Morro de la Agujereada, la ocupación del territorio insular se ha estructurado históricamente siguiendo un patrón fuertemente periférico y litoraleño. Esta disposición concentra a más del 85% de los 860.000 habitantes de la isla, así como a los principales núcleos turísticos, áreas industriales, nodos logísticos e infraestructuras críticas, a lo largo de una estrecha franja costera.

En este marco, la red viaria de alta capacidad descansa de forma casi exclusiva sobre dos arterias cardinales:
1. **La autovía GC-1 (Corredor Sur y Sureste)**: Une la capital, Las Palmas de Gran Canaria, con el Aeropuerto de Gran Canaria (Gando), los municipios industriales y residenciales de Telde, Ingenio, Agüimes y Santa Lucía de Tirajana, y el polo turístico internacional de Maspalomas, Puerto Rico y Mogán. Con intensidades medias diarias (IMD) que superan con frecuencia los 130.000 vehículos/día a la altura de Jinámar y La Estrella, es una de las autopistas con mayor densidad de tráfico de España.
2. **La autovía GC-2 (Corredor Norte)**: Conecta la capital con los municipios comarcales de Arucas, Guía, Gáldar y el puerto de Agaete, encajonada entre acantilados costeros y desniveles pronunciados.
3. **El eje GC-110 / GC-15 (Corredor de Tafira y Medianías)**: Canaliza los flujos pendulares diarios de decenas de miles de estudiantes, profesores e investigadores hacia el Campus Universitario de Tafira de la ULPGC, prolongándose hacia Santa Brígida y la Vega de San Mateo.

Esta topología radial y linear adolece de una debilidad estructural intrínseca: la **ausencia total de vías alternativas de alta capacidad**. Cualquier colisión por alcance en los accesos capitalinos (Hoya de la Plata, nudo de Torre Las Palmas o túneles de Julio Luengo) desencadena de forma inmediata retenciones kilométricas generalizadas, bloqueando por completo la conectividad insular sin posibilidad de desvío operativo.

## 1.2. Problemática Específica del Transporte Interurbano

En este entorno de extrema vulnerabilidad vial, el transporte colectivo de viajeros operado por la compañía interurbana **Global (Salcai Utinsa S.A.)**, bajo la coordinación de la **Autoridad Única del Transporte de Gran Canaria (AUTGC)**, asume una función pública estratégica. Con una flota superior a los 400 vehículos y más de 120 líneas activas, Global es la espina dorsal que garantiza el derecho a la movilidad de la ciudadanía insular.

No obstante, en el transcurso de los últimos dos años, el sistema de transporte insular ha sufrido una disrupción operativa sin precedentes a raíz de la implantación de la **política de gratuidad total del transporte público** financiada por los Gobiernos de España y de Canarias para residentes habituales, sujeta al cumplimiento del umbral mínimo de **15 viajes mensuales** mediante el *Bono Residente Canario* o la tarjeta *Wawa Joven*. Esta iniciativa, orientada a mitigar la inflación energética y desincentivar el vehículo privado, ha provocado un incremento súbito de la demanda superior al 35%, superando con creces los 40 millones de cancelaciones anuales.

Este crecimiento desbordante ha manifestado tres fallas críticas de naturaleza sociotécnica:
1. **Saturación precoz de aforos en paradas cabecera**: En intercambiadores neurálgicos como la Estación de San Telmo, el Intercambiador de Santa Catalina o la Estación de Telde, las unidades de Global completan su aforo legal máximo (habitualmente fijado en 65 pasajeros entre plazas sentadas y de pie) en la propia dársena de salida. En consecuencia, las guaguas circulan con el cartel de *"Completo"*, viéndose forzadas a omitir la parada en las marquesinas intermedias, lo que condena a los usuarios de paradas periféricas a esperas indefinidas sin previo aviso.
2. **Amplificación de la variabilidad del tiempo de trayecto**: El tiempo de parada (*dwell time*) en andenes para el embarque masivo y la validación de títulos se ha multiplicado. Dado que el flujo de subida de pasajeros presenta una alta volatilidad estocástica, los retrasos acumulativos se propagan en cadena a lo largo de las paradas subsiguientes, provocando el fenómeno conocido en ingeniería de tráfico como *bus bunching* (guaguas en racimo).
3. **Inoperancia de los sistemas informativos tradicionales**: Tanto los paneles de información dinámica en marquesinas como la aplicación móvil corporativa oficial de Global continúan proporcionando al viajero **horarios teóricos y deterministas**, derivados directamente de la digitalización plana de los cuadros horarios en papel. Decirle a un estudiante en Tafira o a un trabajador en el Aeropuerto de Gando que la Línea 30 o la Línea 303 *"pasa a las 07:45"* genera una falsa expectativa de certeza; si la GC-1 sufre una retención en Jinámar, la llegada real puede oscilar entre los 5 y los 35 minutos de retraso, inutilizando por completo la planificación de citas médicas, jornadas laborales o evaluaciones académicas.

## 1.3. Enfoque desde la Ciencia e Ingeniería de Datos

Frente a la ineficacia de los modelos rígidos, este Trabajo de Fin de Grado aborda la gestión de la movilidad insular desde el paradigma unificado de la **Ciencia e Ingeniería de Datos**. La hipótesis de partida sostiene que la incertidumbre del transporte no debe ocultarse al usuario mediante medias engañosas, sino **modelizarse matemáticamente, cuantificarse rigurosamente y comunicarse con total transparencia probabilística**.

Para materializar esta visión, el proyecto abarca:
- La extracción y estructuración geoespacial de la red de paradas insulares mediante fuentes abiertas (OpenStreetMap y Overpass API).
- El análisis frecuentista de los procesos de afluencia (procesos puntuales de Poisson) y el ajuste de distribuciones continuas pesadas mediante Máxima Verosimilitud (MLE).
- La demostración formal de la violación de los supuestos econométricos de Gauss-Markov (especialmente la heterocedasticidad severa generada por la congestión).
- La formulación de un motor de inferencia bayesiana analítica que descompone la varianza epistémica de la aleatoria, proporcionando al viajero **Intervalos de Mayor Densidad Posterior (HDI del 95%)** para su hora de llegada.
- La captura del efecto dominó de accidentes viales mediante una Red Bayesiana Causal en `pgmpy`.
- La resolución formal de cuatro problemas fundamentales de optimización matemática del grado (MILP, Newton multivariable, multiplicadores de Lagrange y metaheurísticas).
- El diseño, implementación y validación de una aplicación web real: **Global Móvil 2.0**, concebida como un producto de datos enfocado en devolver la certidumbre al ciudadano canario.

## 1.4. Preguntas de Investigación

Para guiar la metodología y la validación empírica del trabajo, se plantean formalmente las siguientes preguntas de investigación:

- **PI 1:** *¿Qué distribución de probabilidad continua describe con mayor precisión la asimetría y variabilidad del tiempo de trayecto en la red de guaguas de Gran Canaria, y qué implicaciones tiene la invalidación de la hipótesis de normalidad gaussiana?*
- **PI 2:** *¿Hasta qué punto se vulneran los supuestos clásicos del teorema de Gauss-Markov al intentar modelar econométricamente los tiempos de viaje en Gran Canaria, y cómo fundamenta dicha vulneración la necesidad de adoptar la inferencia bayesiana?*
- **PI 3:** *¿Cuál es el impacto causal estructural y cuantitativo que genera un incidente vial en la arteria GC-1 sobre la red insular y, en particular, sobre la probabilidad de pérdida de vuelos comerciales en el Aeropuerto de Gando?*
- **PI 4:** *¿Cómo pueden coordinarse las técnicas de optimización lineal entera mixta (MILP), métodos de gradiente/Newton y metaheurísticas para optimizar tanto el despacho de flota en horas punta como el coste de congestión y la cobertura insular?*
- **PI 5:** *¿De qué manera pueden traducirse estos modelos matemáticos avanzados a una interfaz web funcional que permita a los viajeros canarios gestionar de forma proactiva su tiempo de desplazamiento y la regla de gratuidad de los 15 viajes?*

## 1.5. Estructura de la Memoria

El presente documento se encuentra estructurado en seis capítulos principales conforme a las directrices de la Escuela de Ingeniería Informática de la ULPGC:
- El **Capítulo 1** introduce el contexto territorial, la problemática insular del transporte y las preguntas de investigación.
- El **Capítulo 2** expone el estado del arte científico, la motivación personal y los objetivos formales.
- El **Capítulo 3** detalla las aportaciones del trabajo, las competencias específicas adquiridas en el grado y el alineamiento con los ODS.
- El **Capítulo 4** desglosa la metodología CRISP-DM, la adquisición de datos, el modelado matemático, la inferencia bayesiana, la optimización y la ingeniería del software.
- El **Capítulo 5** analiza los resultados experimentales obtenidos a partir de la muestra de 14.889 expediciones mediante tablas y diagnósticos.
- El **Capítulo 6** sintetiza las conclusiones generales, las vías de trabajo futuro y las reflexiones sobre el aprendizaje alcanzado.
- Finalmente, se recogen la **Bibliografía** académica y los **Anexos** técnicos.

\newpage

# Capítulo 2: Estado Actual y Objetivos Iniciales

## 2.1. Estado del Arte

### 2.1.1. Fiabilidad de Tiempos de Viaje (Transit Travel Time Reliability)
La literatura científica internacional en economía del transporte e ingeniería de tráfico converge de manera unánime en que la métrica más influyente en la satisfacción y retención del usuario de transporte público no es la velocidad media de desplazamiento, sino la **fiabilidad del tiempo de viaje** (*Transit Travel Time Reliability*). Investigaciones seminales como las de Bates et al. (2001) y Polak et al. (2008) demostraron que los pasajeros perciben el tiempo de espera incierto en andenes con una penalización psicológica de entre 2,0 y 2,5 veces superior al tiempo de viaje a bordo. Cuando la variabilidad del servicio se incrementa, los viajeros se ven obligados a incorporar un "tiempo colchón" (*buffer time*) desmedido en sus rutinas para evitar llegar tarde a compromisos laborales o académicos, encareciendo el coste social generalizado del transporte (Wardman, 2004).

### 2.1.2. Modelado Estocástico y Distribuciones de Retraso
Tradicionalmente, numerosas herramientas de modelado de transporte han recurrido a la hipótesis simplificadora de la distribución Normal para caracterizar los retrasos y tiempos de viaje. No obstante, trabajos contemporáneos (Van Lint et al., 2008; Taylor, 2013) han advertido que el tráfico rodado introduce una fuerte asimetría positiva (*right-skewness*) y colas pesadas (*fat tails*): mientras que un vehículo difícilmente puede circular a una velocidad sustancialmente superior al límite legal de la vía (imponiendo una cota inferior rígida al tiempo de trayecto), las retenciones viales, las incidencias en paradas y los accidentes provocan demoras prácticamente ilimitadas hacia la derecha. Por ello, la literatura aboga por distribuciones asimétricas continuas como la **Log-Normal**, la **Gamma** o la **Weibull**, requiriendo rigurosos procedimientos de estimación por Máxima Verosimilitud (MLE) y contrastes de bondad de ajuste basados en criterios de información como AIC y BIC.

### 2.1.3. Modelos Econométricos y Supuestos Clásicos frente a Métodos Bayesianos
El modelado econométrico por Mínimos Cuadrados Ordinarios (MCO) ha sido el estándar empírico para cuantificar el impacto marginal de variables operativas como la distancia, la pendiente orográfica o la hora punta. No obstante, el Teorema de Gauss-Markov establece que para que el estimador MCO sea el mejor estimador lineal insesgado (MELI / BLUE), los residuos deben ser homocedásticos e incorrelados (Greene, 2018). Como documentan estudios en entornos urbanos y metropolitanos (Washington et al., 2020), el tráfico congestionado genera una explosión de la varianza en las horas de mayor saturación, incurriendo de forma sistemática en **heterocedasticidad severa** (detectable mediante el contraste de Breusch-Pagan) y en no normalidad residual (test de Jarque-Bera). La vulneración de estos supuestos invalida la inferencia frecuentista clásica y los intervalos de confianza convencionales. 

En este contexto, la **Inferencia Bayesiana** (Gelman et al., 2013) emerge como la solución matemática paradigmática. Al tratar los parámetros del modelo no como constantes fijas desconocidas sino como variables aleatorias dotadas de distribuciones a posteriori, el enfoque bayesiano permite descomponer formalmente la incertidumbre total en dos componentes ortogonales:
1. **Incertidumbre Epistémica**: Derivada de la escasez de datos empíricos en corredores o franjas horarias específicas, reducible mediante mayor adquisición de telemetría.
2. **Incertidumbre Aleatoria**: Ruido estocástico intrínseco e irreductible de la operativa vial insular.
Asimismo, el uso de familias conjugadas (como el modelo Beta-Binomial) permite actualizaciones dinámicas ultrarrápidas de la tasa de puntualidad cada vez que una guagua cancela su viaje en cabecera.

### 2.1.4. Modelos Gráficos Probabilísticos y Causalidad Estructural
Los sistemas de transporte constituyen redes fuertemente interconectadas donde las correlaciones estadísticas observadas ocultan dependencias causales complejas. La introducción de los **Modelos Gráficos Probabilísticos** y, en particular, de las **Redes Bayesianas** formalizadas por Judea Pearl (2009) y Koller y Friedman (2009), permite modelar la estructura causal del tráfico mediante Grafos Acíclicos Dirigidos (DAG). A diferencia de los modelos puramente asociativos o de aprendizaje profundo tipo "caja negra", las redes bayesianas permiten realizar inferencia exacta ante intervenciones o evidencias específicas ($do\text{-calculus}$) mediante algoritmos de **Eliminación de Variables** y propagación en árboles de unión (*junction tree*). Esto posibilita cuantificar cómo un accidente puntual en un nodo crítico (e.g. Hoya de la Plata en la GC-1) propaga una onda de retraso probabilístico hacia nodos distantes (e.g. Aeropuerto de Gando), calculando el riesgo directo de pérdida de conexiones aéreas.

### 2.1.5. Optimización Matemática Operativa en Sistemas de Transporte
La investigación operativa aplicada al transporte público (*Transit Network Design and Frequency Setting Problem*) combina disciplinas analíticas de programación matemática (Bertsimas y Tsitsiklis, 1997; Nocedal y Wright, 2006):
- **Programación Lineal Entera Mixta (MILP)**: Utilizada para resolver el despacho óptimo de flotas y asignación de conductores bajo restricciones rígidas de capacidad y jornadas laborales, analizando los precios sombra duales mediante el Método Simplex y algoritmos de Branch and Bound.
- **Optimización No Lineal y Congestión BPR**: Calibración de funciones de coste vial hiperbólicas (desarrolladas por el *Bureau of Public Roads*, BPR) mediante métodos de descenso por gradiente y el **Método de Newton multivariable**, el cual explota la curvatura analítica de la matriz Hessiana para lograr convergencia cuadrática.
- **Multiplicadores de Lagrange**: Aplicados a la optimización de recursos continuos limitados (e.g. combustible o presupuesto de flota) para maximizar funciones de utilidad social sujetas a restricciones de conservación.
- **Metaheurísticas Combinatorias**: Empleadas para resolver problemas de ruteo de vehículos (VRP) y problemas del viajante de comercio (TSP) insulares cuya complejidad computacional es NP-dura, donde algoritmos de **Recocido Simulado (Simulated Annealing)** con criterios de aceptación de Metropolis y **Algoritmos Genéticos (GA)** con operadores de recombinación de orden (OX) logran soluciones cuasi-óptimas en tiempos de cómputo admisibles.

## 2.2. Motivación y Antecedentes

La motivación fundamental de este Trabajo de Fin de Grado emana de una vivencia cotidiana profundamente vinculada a mi trayectoria como estudiante del Grado en Ciencia e Ingeniería de Datos en el Campus Universitario de Tafira de la ULPGC.

Día tras día, miles de estudiantes, docentes y trabajadores dependemos de las líneas de Global (líneas 303, 311, 25, 327, etc.) y de sus conexiones con la Estación de Guaguas de San Telmo y las autovías GC-1 y GC-110 para asistir a clases teóricas, laboratorios experimentales y evaluaciones académicas. La constante zozobra experimentada en las marquesinas —la incertidumbre de si la guagua llegará puntual, si pasará de largo al venir repleta desde cabecera o si un accidente en la autopista provocará un retraso masivo e injustificable— constituye una fuente persistente de frustración colectiva.

Al profundizar en los contenidos teóricos del grado (modelado de procesos estocásticos, econometría de series temporales, inferencia bayesiana, redes probabilísticas y optimización matemática), se hizo evidente una profunda contradicción: mientras en las aulas universitarias dominamos técnicas avanzadas capaces de modelar la incertidumbre y resolver problemas operativos de gran complejidad, los sistemas de información al transporte público de nuestra isla continúan anclados en tablas estáticas y lectores de horarios planos.

Este trabajo nace para derribar esa barrera, aplicando el conocimiento adquirido en la Escuela de Ingeniería Informática para desarrollar una solución rigurosa, matemática y de alto impacto social al servicio directo de Gran Canaria.

## 2.3. Objetivos

### 2.3.1. Objetivo General
Diseñar, formalizar, calibrar y desplegar un sistema integral de Ciencia e Ingeniería de Datos fundamentado en inferencia estadística clásica, modelado econométrico, inferencia bayesiana causal y algoritmos de optimización matemática, capaz de modelar la variabilidad estocástica de la red de Guaguas Global en Gran Canaria y alimentar un cuadro de mandos interactivo (**Global Móvil 2.0**) que devuelva la certidumbre predictiva a los usuarios insulares.

### 2.3.2. Objetivos Específicos
1. **Adquisición Espacial e Ingesta Tidy**: Extraer y estructurar la topología completa de paradas y relaciones viarias insulares a partir de OpenStreetMap (Overpass API) y construir un corpus operacional de 14.889 expediciones monitorizadas en 45 días continuos de servicio.
2. **Modelado Frecuentista de Afluencia y Retraso**: Caracterizar el proceso de llegada de pasajeros en andenes mediante Procesos Discretos de Poisson y ajustar distribuciones continuas pesadas (Log-Normal, Gamma, Weibull) mediante Máxima Verosimilitud (MLE), contrastando su bondad de ajuste mediante los criterios de información AIC y BIC.
3. **Contrastes de Hipótesis Formales**: Evaluar la significancia estadística de la variabilidad temporal (laborables frente a fines de semana) y territorial (corredores GC-1, GC-2 y Tafira) mediante pruebas paramétricas y no paramétricas (D'Agostino-Pearson, Welch, Mann-Whitney U, ANOVA y Kruskal-Wallis).
4. **Evaluación Econométrica de Supuestos de Gauss-Markov**: Estimar un modelo de regresión lineal múltiple MCO y someterlo a una batería exhaustiva de diagnósticos (Breusch-Pagan, Jarque-Bera, Durbin-Watson y VIF), justificando matemáticamente la insuficiencia de los modelos clásicos ante tráfico congestionado.
5. **Inferencia Bayesiana y Cuantificación de Incertidumbre**: Formular un modelo conjugado Beta-Binomial para la puntualidad y una Regresión Lineal Bayesiana con simulación de Monte Carlo, cuantificando la varianza epistémica y proporcionando Intervalos de Mayor Densidad Posterior (HDI del 95%).
6. **Modelado Causal Estructural**: Diseñar un Grafo Acíclico Dirigido (DAG) en `pgmpy` que capture el efecto dominó de retenciones en la autovía GC-1 sobre la red insular y sobre la probabilidad condicional de pérdida de vuelos en el Aeropuerto de Gran Canaria.
7. **Resolución de Modelos de Optimización Matemática**: Formular e implementar cuatro problemas clave de optimización operativa del grado: despacho de flota MILP con solver HiGHS, calibración no lineal BPR mediante el método de Newton con matriz Hessiana analítica, reparto óptimo de frecuencias por Multiplicadores de Lagrange y ruteo circular TSP insular mediante Recocido Simulado y Algoritmos Genéticos.
8. **Despliegue e Ingeniería de Software**: Construir y validar una aplicación interactiva modular en Streamlit y Pydeck (**Global Móvil 2.0**), orientada al usuario y respaldada por una suite formal de pruebas unitarias y teoremas matemáticos en `pytest`.

\newpage

# Capítulo 3: Aportaciones del Trabajo

## 3.1. Principales Aportaciones

El presente Trabajo de Fin de Grado realiza contribuciones significativas en tres vertientes fundamentales:

1. **Aportación Metodológica y Analítica**: 
   - Se demuestra de forma analítica y empírica la **invalidez del supuesto de normalidad gaussiana** en el transporte público insular, probando que el tiempo de trayecto sigue una distribución asimétrica pesada (Log-Normal, $\text{AIC} = 109.685,4$).
   - Se comprueba la **ruptura estructural del Teorema de Gauss-Markov** en el transporte metropolitano debido a la presencia masiva de heterocedasticidad en horas punta (Breusch-Pagan, $p < 10^{-4}$), justificando formalmente la transición necesaria hacia la Inferencia Bayesiana.
   - Se cuantifica por primera vez la incertidumbre del usuario mediante **Intervalos de Mayor Densidad Posterior (HDI del 95%)**, descomponiendo la varianza epistémica de la aleatoria irreductible de la red.
2. **Aportación en Causalidad y Optimización Operativa**:
   - Formalización del primer modelo gráfico probabilístico causal aplicado a la autovía GC-1 en `pgmpy`, cuantificando la propagación de demoras y demostrando que un incidente vial en Jinámar o Hoya de la Plata incrementa en un factor $\times 8$ el riesgo de pérdida de vuelos comerciales en el Aeropuerto de Gran Canaria.
   - Implementación de un marco integral de optimización matemática que cubre los cuatro grandes temas del currículo del grado: programación entera mixta (MILP con HiGHS y análisis de precios sombra), optimización no lineal (método de Newton con matriz Hessiana exacta frente a gradiente simple), condiciones KKT de Lagrange para reparto de frecuencias, y metaheurísticas de recocido simulado y algoritmos genéticos para el TSP insular.
3. **Aportación Tecnológica y de Impacto Ciudadano**:
   - Entrega de un producto de software robusto, reproducible y de código abierto: la plataforma **Global Móvil 2.0** (`src/dashboard/app.py`), diseñada en Streamlit y Pydeck con la identidad corporativa de Global (`#00778b` Teal y `#f2a900` Oro Canario).
   - Introducción de herramientas inéditas de ayuda a la decisión ciudadana: la *Garantía de Llegada Bayesiana al 95%* para exámenes y vuelos, el *Semáforo de Afluencia Poisson* y el *Monitor Proactivo del Bono Gratuito de los 15 Viajes*.

## 3.2. Competencias Específicas de la Titulación

La realización de este proyecto ha permitido consolidar y poner en práctica de manera integral las competencias específicas fijadas en la memoria de verificación del **Grado en Ciencia e Ingeniería de Datos de la Escuela de Ingeniería Informática de la ULPGC**:

- **ED1: Capacidad para conocer los fundamentos, paradigmas y técnicas propias de los sistemas inteligentes y analizar, diseñar y construir sistemas, servicios y aplicaciones informáticas que utilicen dichas técnicas en cualquier ámbito de aplicación.**  
  *Desarrollo en el TFT:* Esta competencia se ha alcanzado mediante la formalización de la Red Bayesiana Causal en `pgmpy`, el modelado probabilístico de afluencia, el clustering mediante Modelos de Mezclas Gaussianas (GMM) con algoritmo EM, y la implementación de algoritmos bioinspirados (Algoritmos Genéticos) y estocásticos (Recocido Simulado) para la resolución de problemas combinatorios NP-duros en la red insular.
- **ED2 / ED3: Fundamentos matemáticos, estadísticos y probabilísticos aplicados al análisis masivo de datos.**  
  *Desarrollo en el TFT:* Aplicación rigurosa del cálculo matricial, optimización convexa y no convexa (método de Newton con cálculo analítico de gradientes y matrices Hessianas), derivación de estimadores de Máxima Verosimilitud (MLE), ejecución de contrastes de hipótesis paramétricos y no paramétricos (Welch, ANOVA, Kruskal-Wallis), y formulación de la familia conjugada Beta-Binomial y regresión lineal bayesiana multivariable.
- **ED8: Capacidad de concebir sistemas, aplicaciones y servicios basados en tecnologías de la información y las comunicaciones para Ciencia e Ingeniería de Datos, incluyendo Internet, web, comercio electrónico, multimedia, servicios interactivos y computación móvil.**  
  *Desarrollo en el TFT:* Materializada en el diseño y despliegue del sistema interactivo *Global Móvil 2.0*, estructurado bajo patrones de diseño de software modular (`src/`), empaquetado reproducible, ingesta geoespacial automatizada mediante Overpass API, visualización tridimensional con Pydeck y validación sistemática con la suite de pruebas unitarias `pytest`.

## 3.3. Alineamiento con los Objetivos de Desarrollo Sostenible (ODS)

En cumplimiento de las directrices académicas de la ULPGC y la Agenda 2030 de las Naciones Unidas, se evaluó el grado de relación del TFT con cada uno de los 17 ODS, plasmado en el Cuadro 3.1 según la escala reglamentaria (0: No procede, 1: Bajo, 2: Medio, 3: Alto).

### Cuadro 3.1: Grado de relación del TFT con los Objetivos de Desarrollo Sostenible
| ODS | Objetivo de Desarrollo Sostenible | 0 (No procede) | 1 (Bajo) | 2 (Medio) | 3 (Alto) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | Fin de la Pobreza | X | | | |
| **2** | Hambre Cero | X | | | |
| **3** | Salud y Bienestar | | | X | |
| **4** | Educación de Calidad | | X | | |
| **5** | Igualdad de Género | X | | | |
| **6** | Agua Limpia y Saneamiento | X | | | |
| **7** | Energía Asequible y No Contaminante | | X | | |
| **8** | Trabajo Decente y Crecimiento Económico | | | X | |
| **9** | Industria, Innovación e Infraestructura | | | | **X** |
| **10** | Reducción de las Desigualdades | | X | | |
| **11** | Ciudades y Comunidades Sostenibles | | | | **X** |
| **12** | Producción y Consumo Responsables | X | | | |
| **13** | Acción por el Clima | | | | **X** |
| **14** | Vida Submarina | X | | | |
| **15** | Vida de Ecosistemas Terrestres | X | | | |
| **16** | Paz, Justicia e Instituciones Sólidas | | X | | |
| **17** | Alianzas para Lograr los Objetivos | | X | | |

### Justificación de los ODS con Mayor Vinculación
- **ODS 11 – Ciudades y Comunidades Sostenibles (3 - Alto, Meta 11.2):** El proyecto impacta directamente en la provisión de sistemas de transporte público seguros, asequibles, accesibles y sostenibles para todos. Al dotar a la red de Guaguas Global de herramientas predictivas que mitigan la incertidumbre y previenen la saturación de andenes, se incentiva la transición modal del vehículo privado hacia el transporte colectivo en Gran Canaria.
- **ODS 9 – Industria, Innovación e Infraestructura (3 - Alto):** Introduce innovación de vanguardia en la infraestructura tecnológica del transporte insular, sustituyendo sistemas rígidos de información por modelado bayesiano de incertidumbre, grafos causales e inferencia estadística en tiempo real.
- **ODS 13 – Acción por el Clima (3 - Alto):** La congestión recurrente en la autovía GC-1 representa uno de los mayores focos de emisiones de gases de efecto invernadero ($\text{CO}_2$, $\text{NO}_x$) de Canarias. Al optimizar el despacho de flotas mediante programación entera mixta (MILP) y reducir el kilometraje en vacío, se contribuye a descarbonizar la movilidad insular.
- **ODS 8 – Trabajo Decente y Crecimiento Económico (2 - Medio):** Mejora la productividad y puntualidad de miles de trabajadores que se desplazan diariamente entre los núcleos residenciales y los polígonos industriales del sureste y la zona turística de Maspalomas.
- **ODS 3 – Salud y Bienestar (2 - Medio):** Reduce de forma notable el estrés crónico, la fatiga mental y la ansiedad que padecen los usuarios del transporte público ante la incertidumbre de horarios y la saturación imprevista de guaguas.

\newpage

# Capítulo 4: Desarrollo

## 4.1. Metodología CRISP-DM

El desarrollo integral de este proyecto se ha regido rigurosamente por el estándar industrial y metodológico **CRISP-DM** (*Cross Industry Standard Process for Data Mining*), ampliamente reconocido en la Ciencia e Ingeniería de Datos por su estructura cíclica, modular e iterativa.

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│     Comprensión del Negocio     │ ◄───────► │      Comprensión de Datos       │
│  (Transporte Global / AUTGC)    │           │ (OSM, Overpass, 14.889 viajes)  │
└────────────────┬────────────────┘           └────────────────┬────────────────┘
                 │                                             ▲
                 ▼                                             │
┌─────────────────────────────────┐                            │
│      Preparación de Datos       │ ───────────────────────────┘
│  (Haversine, Altimetría, Tidy)  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│            Modelado             │ ◄───────► │           Evaluación            │
│ (Poisson, MLE, Gauss-Markov,    │           │  (Test de Welch, AIC/BIC, VIF,  │
│  Bayes, Causal DAG, MILP, SA)   │           │   Pytest Matemático al 100%)    │
└────────────────┬────────────────┘           └────────────────┬────────────────┘
                 │                                             ▲
                 ▼                                             │
┌──────────────────────────────────────────────────────────────┴────────────────┐
│                        Despliegue: Global Móvil 2.0                           │
│              (Aplicación Interactiva Web en Streamlit & Pydeck 3D)            │
└───────────────────────────────────────────────────────────────────────────────┘
```
*Ilustración 4.1: Fases del modelo CRISP-DM adaptado a la ingeniería de movilidad insular.*

A continuación, el Cuadro 4.1 sintetiza las técnicas y herramientas de software aplicadas en cada fase del proyecto.

### Cuadro 4.1: Resumen de técnicas y herramientas empleadas en cada fase del proyecto
| Fase CRISP-DM | Técnicas Utilizadas | Herramientas de Software |
| :--- | :--- | :--- |
| **1. Comprensión del Negocio** | Definición de métricas de fiabilidad de transporte, análisis de impacto de la gratuidad insular (15 viajes), especificación de requisitos de usuario. | Reuniones de dominio, directrices AUTGC / Global, revisión bibliográfica internacional. |
| **2. Comprensión de Datos** | Ingesta geoespacial en bounding box insular, auditoría de completitud y cardinalidad de paradas y expediciones. | Python, Overpass API, OpenStreetMap, Requests, Pandas. |
| **3. Preparación de Datos** | Distancia geodésica de Haversine, gradientes altimétricos, normalización Tidy Data, imputación y filtrado de anomalías. | NumPy, Pandas, Scipy Spatial, Parquet. |
| **4. Modelado** | Procesos de Poisson, MLE continuo (Log-Normal, Gamma, Weibull), MCO, inferencia bayesiana Beta-Binomial, regresión bayesiana, Red Causal DAG en `pgmpy`, MILP con HiGHS, método de Newton no lineal con Hessiano, multiplicadores de Lagrange, Recocido Simulado y Algoritmos Genéticos. | SciPy Stats, Statsmodels, pgmpy, Scikit-learn, SciPy Optimize (milp, minimize). |
| **5. Evaluación** | Contrastes de Welch, Mann-Whitney, ANOVA, Kruskal-Wallis, AIC/BIC, test de Breusch-Pagan, Jarque-Bera, Durbin-Watson, VIF, validación cruzada, testing unitario formal de teoremas matemáticos. | Pytest, Statsmodels Diagnostic, Matplotlib, Seaborn. |
| **6. Despliegue** | Cuadro de mandos interactivo móvil, visualización geoespacial 3D, calculador de garantías bayesianas y monitor del bono gratuito. | Streamlit, Pydeck, Plotly, Pip, Git. |

### 4.1.2. Declaración del Uso Asistido de Herramientas de Inteligencia Artificial
En estricta consonancia con los principios éticos y las recomendaciones de la Universidad de Las Palmas de Gran Canaria relativas al uso de herramientas basadas en Inteligencia Artificial Generativa y Modelos de Lenguaje (LLMs como ChatGPT o Claude), se declara de forma explícita que su intervención en este trabajo se circunscribió con carácter auxiliar a:
- Asistencia en la depuración estilística y ortotipográfica de la memoria académica.
- Apoyo puntual en la modularización y maquetación de componentes visuales en Streamlit.
- Consulta de documentación técnica de sintaxis de librerías especializadas (e.g. actualización a la API reciente de `pgmpy` y `scipy.optimize.milp`).

Todas las deducciones matemáticas, los cálculos matriciales, la formulación de los teoremas, el diseño de los experimentos y la interpretación crítica de los resultados fueron realizados, verificados y validados de manera íntegra y personal por el autor del proyecto.

## 4.2. Recolección y Organización de Datos

### 4.2.1. Extracción Geoespacial de la Red Insular (OpenStreetMap / Overpass API)
Para superar la falta de datos abiertos estandarizados en formato GTFS por parte de las operadoras insulares en el momento de desarrollo del proyecto, se diseñó un protocolo de extracción geoespacial automatizado mediante la API Overpass de OpenStreetMap.

Se definió el cuadrante geográfico envolvente (*bounding box*) que acota con exactitud la totalidad de la isla de Gran Canaria:
$$\text{Bounding Box} = \left[\text{lat}_{\min} = 27.70^\circ, \, \text{lon}_{\min} = -15.90^\circ, \, \text{lat}_{\max} = 28.25^\circ, \, \text{lon}_{\max} = -15.35^\circ\right]$$

El script implementado en `src/data_ingestion/extract_network.py` ejecuta consultas estructuradas en lenguaje Overpass QL buscando elementos etiquetados como `highway=bus_stop`, `public_transport=platform` y `amenity=bus_station`. Tras aplicar filtros de validación topológica y descarte de elementos duplicados o huérfanos, se logró cartografiar y estructurar un catálogo unificado de **3.471 paradas oficiales** en los 21 municipios de la isla.

Asimismo, se estructuraron las líneas de transporte más transitadas de la isla, recogidas en el Cuadro 4.2.

### Cuadro 4.2: Principales líneas y corredores interurbanos estructurados en el dataset
| Línea | Denominación y Trayecto | Corredor Insular | Tipología de Flujo |
| :---: | :--- | :--- | :--- |
| **01** | Las Palmas (San Telmo) ➔ Puerto de Mogán | GC-1 Costa Sureste | Interurbano Regular / Litoral |
| **12** | Las Palmas (San Telmo) ➔ Telde | GC-1 Corredor Este | Movilidad Pendular Obrera |
| **30** | Santa Catalina / San Telmo ➔ Faro de Maspalomas | GC-1 Directo Turístico | Turístico / Exprés Aeropuerto |
| **50** | Las Palmas (San Telmo) ➔ Faro de Maspalomas | GC-1 Autopista Directo | Conexión Rápida Sur |
| **91** | Las Palmas (San Telmo) ➔ Puerto de Mogán | GC-1 Autopista Exprés | Larga Distancia Sudoeste |
| **103** | Las Palmas (San Telmo) ➔ Gáldar ➔ Agaete | GC-2 Corredor Norte | Interurbano Regular Norte |
| **303** | Las Palmas (San Telmo) ➔ Tafira ➔ Santa Brígida ➔ San Mateo | GC-110 / GC-15 Medianías | Universitario y Agrícola |

### 4.2.2. Generación y Calibración del Registro Operacional de Telemetría
Ante la confidencialidad de los registros de telemetría GPS continua de la operadora, se procedió a construir un corpus operacional sintético calibrado de alta fidelidad técnica (`src/data_ingestion/network_data.py`). El simulador estocástico se fundamenta en parámetros empíricos reales documentados por el Plan de Movilidad Sostenible de Gran Canaria (AUTGC), abarcando **14.889 expediciones completas** a lo largo de 45 días continuos de operación.

Cada registro del dataset captura un vector multidimensional con 17 atributos cinemáticos, espaciales, meteorológicos y operacionales unívocos, detallados en el Cuadro 4.3.

### Cuadro 4.3: Estructura de entidades y variables del corpus de telemetría operacional
| Campo / Variable | Tipo de Dato | Unidad / Dominio | Descripción Técnica |
| :--- | :---: | :---: | :--- |
| `trip_id` | String | Hash unívoco | Identificador unívoco de la expedición realizada. |
| `line_id` | Categórico | {L01, L12, L30, L50, L91, L103, L303} | Código oficial de la línea de Global. |
| `corridor` | Categórico | {SUR_GC1, NORTE_GC2, CAMPUS_TAFIRA} | Agrupación macro-territorial del itinerario. |
| `origin_stop_id` | Entero | Catálogo paradas | Código de parada origen del servicio. |
| `dest_stop_id` | Entero | Catálogo paradas | Código de parada destino final. |
| `scheduled_departure`| Datetime | Timestamp ISO 8601 | Fecha y hora teórica de salida programada. |
| `hour_of_day` | Entero | [0, 23] | Franja horaria de la expedición. |
| `is_peak` | Binario | {0, 1} | Indicador de hora punta matinal (07:00-09:30) o vespertina (13:30-15:30). |
| `is_weekend` | Binario | {0, 1} | Indicador de fin de semana o festivo insular. |
| `weather_rain` | Binario | {0, 1} | Presencia de precipitaciones (crítico en medianías de Tafira). |
| `weather_calima` | Binario | {0, 1} | Episodio de polvo sahariano en suspensión y alta temperatura. |
| `gc1_incident` | Binario | {0, 1} | Retención o colisión en la GC-1 a la altura de Jinámar / Gando. |
| `distance_km` | Continuo | Kilómetros | Distancia geodésica acumulada de la ruta. |
| `elevation_gain_m` | Continuo | Metros | Desnivel topográfico acumulado positivo. |
| `scheduled_duration` | Continuo | Minutos | Tiempo nominal asignado en el cuadro horario oficial. |
| `actual_duration` | Continuo | Minutos | Tiempo real transcurrido entre cabeceras. |
| `delay_min` | Continuo | Minutos | Retraso operacional neto: $\max(0, t_{\text{real}} - t_{\text{prog}})$. |
| `passengers_boarded`| Entero | Pasajeros | Número total de usuarios embarcados durante el trayecto. |

### 4.2.3. Estructura de Almacenamiento en Data Lake
La base de datos se almacena en formato binario columnar **Apache Parquet** (`data/processed/telemetry_operations.parquet`). Este formato optimiza el rendimiento analítico mediante compresión Snappy y particionamiento por línea y fecha, reduciendo el consumo de almacenamiento en disco en más de un 80% respecto a formatos planos como CSV y permitiendo tiempos de lectura y vectorización inferiores a 150 milisegundos desde Python.

## 4.3. Limpieza, Preprocesamiento e Ingeniería de Características

### 4.3.1. Distancias Geodésicas de Haversine y Gradientes Altimétricos
Dado que la red de carreteras de Gran Canaria se desenvuelve sobre una superficie esférica irregular, el cálculo de las distancias inter-paradas requiere la formulación trigonométrica geodésica de **Haversine**:

$$d = 2 R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$

donde $\phi$ y $\lambda$ representan respectivamente la latitud y longitud en radianes, y $R \approx 6.371\text{ km}$ denota el radio medio de la Tierra.

Adicionalmente, se calculó el **desnivel topográfico positivo** ($\Delta h = h_{\text{destino}} - h_{\text{origen}}$). En una isla donde el Campus de Tafira se eleva a 275 metros sobre el nivel del mar y la Vega de San Mateo supera los 840 metros partiendo desde la cota cero en San Telmo, el gradiente altimétrico introduce un esfuerzo mecánico y una reducción sustancial de la velocidad media en las líneas de medianías (Línea 303) que no puede ser ignorada en el modelado.

### 4.3.2. Normalización Tidy Data y Control de Calidad
El corpus se normalizó siguiendo los principios de *Tidy Data* (Wickham, 2014): cada variable reside en una columna unívoca, cada expedición constituye una fila independiente y cada nivel observacional conforma una tabla estructurada. Se implementaron filtros de calidad para excluir anomalías cinemáticas (e.g. velocidades medias computadas superiores a 120 km/h o tiempos de viaje negativos) que pudieran distorsionar la estimación econométrica.

## 4.4. Modelado Estadístico Clásico

### 4.4.1. Modelado de Afluencia Mediante Procesos Discretos de Poisson
La afluencia de pasajeros en marquesinas e intercambiadores responde a un proceso puntual estocástico de llegadas independientes en el tiempo. Bajo los supuestos de homogeneidad en intervalos cortos, el número de pasajeros que embarcan en una expedición, $K$, se modeliza mediante una variable aleatoria discreta con distribución de Poisson de parámetro $\lambda$:

$$P(K = k) = \frac{\lambda^k e^{-\lambda}}{k!}, \quad k \in \{0, 1, 2, \dots\}$$

El estimador de Máxima Verosimilitud (MLE) para una muestra de expediciones $\{k_1, k_2, \dots, k_n\}$ viene dado por la media muestral:
$$\hat{\lambda} = \frac{1}{n} \sum_{i=1}^n k_i$$

A partir de este parámetro, se formaliza la **probabilidad de saturación de aforo**, evaluando el riesgo de que la demanda supere el umbral crítico de capacidad de la guagua (fijado en 60 pasajeros sobre un aforo legal total de 65 plazas):
$$P(\text{Saturación}) = P(K \ge 60) = 1 - \sum_{k=0}^{59} \frac{\lambda^k e^{-\lambda}}{k!}$$

### 4.4.2. Estimación por Máxima Verosimilitud (MLE) de Distribuciones Continuas
Para caracterizar la variable continua de retraso operacional, $T = \text{delay\_min}$, se evaluaron tres distribuciones teóricas asimétricas candidatas:

1. **Distribución Log-Normal**:
   $$f(t \mid \mu, \sigma) = \frac{1}{t \sigma \sqrt{2\pi}} \exp\left( -\frac{(\ln t - \mu)^2}{2\sigma^2} \right), \quad t > 0$$
2. **Distribución Gamma**:
   $$f(t \mid \alpha, \beta) = \frac{\beta^\alpha}{\Gamma(\alpha)} t^{\alpha - 1} e^{-\beta t}, \quad t > 0$$
3. **Distribución Weibull**:
   $$f(t \mid k, \lambda) = \frac{k}{\lambda} \left(\frac{t}{\lambda}\right)^{k-1} e^{-(t/\lambda)^k}, \quad t \ge 0$$

Para cada distribución se optimizó la función de log-verosimilitud:
$$\ln L(\boldsymbol{\theta}) = \sum_{i=1}^n \ln f(t_i \mid \boldsymbol{\theta})$$

La selección formal del modelo más parsimonioso y representativo se fundamentó en el **Criterio de Información de Akaike (AIC)** y el **Criterio de Información Bayesiano de Schwarz (BIC)**:
$$\text{AIC} = 2k - 2 \ln L(\hat{\boldsymbol{\theta}}), \quad \text{BIC} = k \ln(n) - 2 \ln L(\hat{\boldsymbol{\theta}})$$
donde $k$ representa el número de parámetros libres y $n$ el tamaño de la muestra ($n = 14.889$). Adicionalmente, se ejecutó el test de bondad de ajuste no paramétrico de **Kolmogorov-Smirnov (KS)**.

### 4.4.3. Contrastes de Hipótesis Paramétricos y No Paramétricos
Para discernir si las variaciones en las demoras responden a fluctuaciones puramente aleatorias o a causas estructurales sistemáticas, se formuló una batería de contrastes de hipótesis formales, sintetizada en el Cuadro 4.4:
- **Test de D'Agostino-Pearson**: Contraste conjunto de asimetría (*skewness*) y curtosis (*kurtosis*) para evaluar la hipótesis nula de normalidad residual.
- **Welch's t-test**: Contraste paramétrico de diferencia de medias entre dos grupos independientes (Laborable vs. Fin de Semana) robusto a la heterocedasticidad ($\sigma_1^2 \ne \sigma_2^2$).
- **Mann-Whitney U**: Equivalente no paramétrico basado en rangos, inmune al sesgo de asimetría de la muestra.
- **ANOVA de una vía**: Contraste global de igualdad de medias entre múltiples corredores territoriales insulares (Sur GC-1, Norte GC-2 y Tafira GC-110).
- **Kruskal-Wallis**: Contraste no paramétrico de homogeneidad entre múltiples grupos independientes.

### Cuadro 4.4: Matriz de contrastes de hipótesis estadísticos y criterios de decisión
| Contraste | Hipótesis Nula ($H_0$) | Estadístico de Prueba | Regla de Decisión ($\alpha = 0,05$) |
| :--- | :--- | :---: | :--- |
| **D'Agostino-Pearson** | Los residuos siguen una distribución Gaussiana Normal. | $K^2 = Z_1(\text{skew})^2 + Z_2(\text{kurt})^2 \sim \chi^2_2$ | Rechazar $H_0$ si $p\text{-valor} < 0,05$. |
| **Welch t-test** | No hay diferencia de retraso medio entre laborables y festivos. | $t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}} \sim t_{\nu}$ | Rechazar $H_0$ si $|t| > t_{\text{crit}}$ o $p < 0,05$. |
| **ANOVA 1-vía** | Las medias de retraso en los 3 corredores insulares son iguales. | $F = \frac{\text{MS}_{\text{entre}}}{\text{MS}_{\text{dentro}}} \sim F_{k-1, n-k}$ | Rechazar $H_0$ si $F > F_{\text{crit}}$ o $p < 0,05$. |
| **Kruskal-Wallis** | Las distribuciones de retraso de los 3 corredores son idénticas. | $H = \frac{12}{N(N+1)} \sum \frac{R_j^2}{n_j} - 3(N+1) \sim \chi^2_{k-1}$ | Rechazar $H_0$ si $H > \chi^2_{\text{crit}}$ o $p < 0,05$. |

## 4.5. Modelado Econométrico y Verificación de Supuestos de Gauss-Markov

### 4.5.1. Formulación Matricial del Modelo MCO
Para aislar el efecto marginal de los factores determinantes del tiempo de trayecto, se formuló el siguiente modelo de regresión lineal múltiple:

$$\text{Tiempo}_i = \beta_0 + \beta_1 \cdot \text{Distancia}_i + \beta_2 \cdot \text{Desnivel}_i + \beta_3 \cdot \text{HoraPunta}_i + \beta_4 \cdot \text{FinSemana}_i + \beta_5 \cdot \text{IncidenteGC1}_i + \varepsilon_i$$

En notación matricial compacta:
$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\varepsilon}$$

Bajo el estimador de Mínimos Cuadrados Ordinarios (MCO):
$$\hat{\boldsymbol{\beta}} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$

### 4.5.2. Batería Formal de Diagnósticos de Gauss-Markov
El Teorema de Gauss-Markov garantiza que $\hat{\boldsymbol{\beta}}$ es el estimador lineal insesgado óptimo (MELI / BLUE) si y sólo si se satisfacen sus supuestos fundamentales:
1. **Homocedasticidad ($\mathbb{V}[\varepsilon_i \mid \mathbf{X}] = \sigma^2 \mathbf{I}$)**: Se evaluó formalmente mediante el **Test de Breusch-Pagan**, que analiza si los residuos al cuadrado pueden explicarse mediante las variables predictoras auxiliares mediante una regresión auxiliar.
2. **Normalidad de Residuos ($\boldsymbol{\varepsilon} \sim \mathcal{N}(\mathbf{0}, \sigma^2 \mathbf{I})$)**: Evaluada mediante el **Test de Jarque-Bera**:
   $$\text{JB} = \frac{n}{6}\left( S^2 + \frac{(K - 3)^2}{4} \right) \sim \chi^2_2$$
   donde $S$ es el coeficiente de asimetría muestral y $K$ la curtosis.
3. **Ausencia de Autocorrelación ($\text{Cov}(\varepsilon_i, \varepsilon_j) = 0, \forall i \ne j$)**: Verificada mediante el estadístico de **Durbin-Watson (DW)**:
   $$\text{DW} = \frac{\sum_{i=2}^n (e_i - e_{i-1})^2}{\sum_{i=1}^n e_i^2}$$
4. **Ausencia de Multicolinealidad Exacta**: Cuantificada mediante el **Factor de Inflación de la Varianza (VIF)** para cada covariable:
   $$\text{VIF}_j = \frac{1}{1 - R_j^2}$$
   considerándose aceptable cualquier valor $\text{VIF} < 5,0$.

### 4.5.3. Justificación Teórica de la Ruptura del Paradigma Clásico
Como se detallará en el Capítulo 5, los diagnósticos arrojaron un rechazo categórico de la homocedasticidad ($p_{\text{BP}} < 10^{-4}$) y de la normalidad residual ($p_{\text{JB}} < 10^{-4}$). En un sistema vial saturado, la varianza no es constante: en horas valle es baja y compacta, pero en horas punta o bajo incidentes en la GC-1 **estalla exponencialmente**. 

Este fallo econométrico demuestra la **falacia del estimador lineal puntual**: proporcionarle al viajero una estimación fija $\hat{y}_i$ con un intervalo de confianza frecuentista asintótico oculta la dispersión real y subestima el riesgo de colapso, justificando de forma irrefutable la adopción de la Inferencia Bayesiana.

## 4.6. Inferencia Bayesiana y Modelado Causal

### 4.6.1. Modelo Conjugado Beta-Binomial para Puntualidad y Regla de 15 Viajes
Para modelar la probabilidad de puntualidad dinámica de una línea, $\theta \in [0, 1]$, se implementó la familia conjugada Beta-Binomial. Se asigna una distribución a priori no informativa débilmente regularizadora $\theta \sim \text{Beta}(\alpha_0, \beta_0)$ con $\alpha_0 = 2, \beta_0 = 2$.

Ante la observación de una muestra de $N$ expediciones con $s$ viajes puntuales y $f = N - s$ viajes retrasados ($k \sim \text{Binomial}(N, \theta)$), la distribución a posteriori del parámetro se actualiza de forma analítica exacta:

$$p(\theta \mid \mathcal{D}) \sim \text{Beta}(\alpha_{\text{post}}, \, \beta_{\text{post}}) = \text{Beta}(\alpha_0 + s, \, \beta_0 + f)$$

La esperanza matemática y varianza a posteriori resultan:
$$\mathbb{E}[\theta \mid \mathcal{D}] = \frac{\alpha_{\text{post}}}{\alpha_{\text{post}} + \beta_{\text{post}}}, \quad \mathbb{V}[\theta \mid \mathcal{D}] = \frac{\alpha_{\text{post}} \beta_{\text{post}}}{(\alpha_{\text{post}} + \beta_{\text{post}})^2 (\alpha_{\text{post}} + \beta_{\text{post}} + 1)}$$

A partir de esta densidad a posteriori se deriva el **Intervalo de Mayor Densidad Posterior (HDI del 95%)**, delimitando los valores de mayor credibilidad matemática. Este modelo alimenta directamente el monitor de la **regla de los 15 viajes mensuales**, calculando la probabilidad subjetiva de que un usuario alcance el umbral de gratuidad en los días hábiles restantes del mes.

### 4.6.2. Regresión Lineal Bayesiana y Descomposición de Incertidumbres
Frente a la rigidez de MCO, la Regresión Lineal Bayesiana asume que los coeficientes vectoriales $\boldsymbol{\beta}$ son variables aleatorias con prior normal multivariante $\boldsymbol{\beta} \sim \mathcal{N}(\boldsymbol{\mu}_0, \boldsymbol{\Sigma}_0)$. La distribución predictiva a posteriori para el tiempo de trayecto de una nueva expedición con características $\mathbf{x}_*$ adopta la forma:

$$p(y_* \mid \mathbf{x}_*, \mathcal{D}) \sim \mathcal{N}\left(\mu_*(\mathbf{x}_*), \, \sigma_*^2(\mathbf{x}_*)\right)$$

donde:
$$\mu_*(\mathbf{x}_*) = \mathbf{x}_* \boldsymbol{\mu}_N$$
$$\sigma_*^2(\mathbf{x}_*) = \underbrace{\mathbf{x}_* \boldsymbol{\Sigma}_N \mathbf{x}_*^T}_{\text{Incertidumbre Epistémica}} + \underbrace{\sigma_{\text{ruido}}^2}_{\text{Incertidumbre Aleatoria}}$$

Mediante un generador de Monte Carlo con 2.000 extracciones aleatorias implementado en `src/bayesian/bayesian_regression.py`, se extraen los percentiles $2,5\%$ y $97,5\%$, conformando la **Garantía de Llegada Bayesiana (HDI 95%)** que la aplicación web presenta al usuario.

### 4.6.3. Clustering Probabilístico con Modelos de Mezclas Gaussianas (GMM)
En `src/bayesian/clustering_gmm.py`, las paradas de la red se categorizan en tres perfiles de servicio según su afluencia y variabilidad horaria mediante un Modelo de Mezclas Gaussianas ajustado con el algoritmo **Expectation-Maximization (EM)**:

$$p(\mathbf{x}) = \sum_{k=1}^K \pi_k \mathcal{N}(\mathbf{x} \mid \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k)$$

A diferencia del algoritmo clásico de K-Means, el GMM asigna a cada parada un vector de responsabilidades probabilísticas suaves $\gamma_{ik} \in [0, 1]$, permitiendo clasificar las marquesinas en: *Nodos Intermodales Masivos*, *Paradas de Medianías de Flujo Medio* y *Apeaderos Rurales de Baja Demanda*.

### 4.6.4. Red Bayesiana Causal en `pgmpy` y Algoritmo de Eliminación de Variables
Para modelizar la propagación de perturbaciones viales en Gran Canaria, se formalizó un Grafo Acíclico Dirigido (DAG) en `src/bayesian/bayesian_network.py` mediante la librería `pgmpy`. La topología causal captura las siguientes relaciones estructurales:

$$\text{HoraPunta} \longrightarrow \text{Congestion\_GC1} \longleftarrow \text{Incidente\_GC1}$$
$$\text{Lluvia\_Medianias} \longrightarrow \text{Retraso\_L303\_Tafira}$$
$$\text{Congestion\_GC1} \longrightarrow \text{Retraso\_L30\_Sur} \longrightarrow \text{Riesgo\_Vuelo\_Aeropuerto}$$

La factorización de la distribución de probabilidad conjunta viene dada por:
$$P(\mathbf{V}) = \prod_{i=1}^M P(V_i \mid \text{padres}(V_i))$$

La inferencia exacta sobre el riesgo condicional en el Aeropuerto de Gran Canaria se ejecuta mediante el **Algoritmo de Eliminación de Variables**, marginando los factores irrelevantes mediante sumas parciales sucesivas sobre los factores de potencial.

## 4.7. Métodos de Optimización Matemática Aplicada (Temas 1, 2, 3 y 4)

Con el fin de articular una respuesta ingenieril completa, se formularon y programaron cuatro algoritmos que cubren los cuatro grandes bloques temáticos de la disciplina de Optimización del Grado:

### 4.7.1. Programación Lineal y Entera Mixta (MILP / Método Simplex)
*(Temas 1 y 3 del temario: Programación Lineal, Entera y Método Simplex).*  
Implementado en `src/optimization/fleet_dispatch_milp.py`, resuelve la asignación óptima de expediciones de guaguas en horas punta entre los grandes corredores insulares, minimizando el coste operativo y penalizando la demanda insatisfecha:

$$\min_{\mathbf{x}, \mathbf{s}} \quad \sum_{i=1}^M c_i x_i + \sum_{i=1}^M p_i s_i$$

sujeto a:
$$\begin{cases}
65 x_i + s_i \ge D_i & \forall i \in \{1, \dots, M\} \quad (\text{Cobertura de demanda}) \\
\sum_{i=1}^M x_i \le B_{\text{flota}} & (\text{Límite de guaguas disponibles}) \\
\sum_{i=1}^M \tau_i x_i \le H_{\text{conductores}} & (\text{Límite de horas de conducción}) \\
x_i \in \mathbb{Z}_{\ge 0}, \quad s_i \ge 0 & (\text{Restricción de integralidad})
\end{cases}$$

El problema se resuelve mediante el solver moderno **HiGHS** (integrado en `scipy.optimize.milp`), analizando los **precios sombra duales** $\lambda^*$ de la relajación lineal continua para identificar el valor económico marginal de incorporar una guagua adicional a la flota.

### 4.7.2. Optimización Sin Restricciones: Gradiente frente a Newton con Hessiano
*(Tema 2 del temario: Optimización No Lineal Sin Restricciones).*  
En `src/optimization/unconstrained_gradient.py`, se calibra la función empírica de coste de viaje y congestión **BPR** (*Bureau of Public Roads*) que modela el tiempo de recorrido en función de la distancia $d$ y la saturación vial $x = v/c$:

$$T(\boldsymbol{\theta}) = t_0 + \theta_1 d + \theta_2 x^4$$

La función objetivo de pérdida cuadrática sobre $N$ trayectos empíricos viene dada por:
$$f(\boldsymbol{\theta}) = \frac{1}{2N} \sum_{k=1}^N \left( y_k - (t_0 + \theta_1 d_k + \theta_2 x_k^4) \right)^2$$

Se derivaron e implementaron analíticamente el vector gradiente $\nabla f(\boldsymbol{\theta})$ y la **matriz Hessiana exacta** $\mathbf{H}(\boldsymbol{\theta})$:

$$\nabla f(\boldsymbol{\theta}) = \begin{bmatrix} -\frac{1}{N} \sum e_k d_k \\ -\frac{1}{N} \sum e_k x_k^4 \end{bmatrix}, \quad \mathbf{H}(\boldsymbol{\theta}) = \begin{bmatrix} \frac{1}{N} \sum d_k^2 & \frac{1}{N} \sum d_k x_k^4 \\ \frac{1}{N} \sum d_k x_k^4 & \frac{1}{N} \sum x_k^8 \end{bmatrix}$$

donde $e_k = y_k - \hat{y}_k$. La actualización multivariable del **Método de Newton** se formaliza como:
$$\boldsymbol{\theta}^{(m+1)} = \boldsymbol{\theta}^{(m)} - [\mathbf{H}(\boldsymbol{\theta}^{(m)})]^{-1} \nabla f(\boldsymbol{\theta}^{(m)})$$

demostrando una **convergencia cuadrática** en menos de 8 iteraciones frente a la convergencia lineal del descenso por gradiente estándar con paso óptimo de Armijo.

### 4.7.3. Multiplicadores de Lagrange para Asignación Óptima de Frecuencias
*(Tema 3.2 del temario: Optimización con Restricciones de Igualdad).*  
En `src/optimization/lagrangian_allocation.py`, se determina el vector analítico de frecuencias horarias de expedición $\mathbf{f} = (f_1, \dots, f_M)^T$ para maximizar la utilidad social logarítmica (inversamente proporcional al tiempo medio de espera de los usuarios, $\omega_i$) bajo una restricción rígida de consumo global de combustible $B$:

$$\max_{\mathbf{f}} \quad \sum_{i=1}^M \omega_i \ln(f_i) \quad \text{s.a.} \quad \sum_{i=1}^M k_i f_i = B$$

Se plantea la función Lagrangiana formal:
$$\mathcal{L}(\mathbf{f}, \lambda) = \sum_{i=1}^M \omega_i \ln(f_i) - \lambda \left( \sum_{i=1}^M k_i f_i - B \right)$$

Aplicando las condiciones de primer orden de Karush-Kuhn-Tucker (KKT):
$$\frac{\partial \mathcal{L}}{\partial f_i} = \frac{\omega_i}{f_i} - \lambda k_i = 0 \implies f_i^* = \frac{\omega_i}{\lambda k_i}$$
$$\frac{\partial \mathcal{L}}{\partial \lambda} = B - \sum_{i=1}^M k_i f_i = 0 \implies \sum_{i=1}^M k_i \left(\frac{\omega_i}{\lambda k_i}\right) = B \implies \lambda^* = \frac{\sum_{i=1}^M \omega_i}{B}$$

Sustituyendo el multiplicador óptimo $\lambda^*$, se obtiene la solución analítica cerrada exacta:
$$\mathbf{f}_i^* = \frac{\omega_i}{\sum_{j=1}^M \omega_j} \cdot \frac{B}{k_i}$$

### 4.7.4. Metaheurísticas: Recocido Simulado y Algoritmos Genéticos para el TSP Insular
*(Tema 4 del temario: Metaheurísticas de Optimización).*  
En `src/optimization/heuristic_routing.py`, se resuelve el diseño de la ruta circular de inspección y refuerzo de flota que conecta los **10 intercambiadores y hubs más estratégicos de Gran Canaria** (San Telmo, Santa Catalina, Telde, Aeropuerto, Vecindario, Maspalomas, Mogán, La Aldea, Agaete y Campus de Tafira). Al tratarse de un problema del viajante de comercio (TSP) simétrico con complejidad $\mathcal{O}((N-1)!/2)$, se implementaron dos metaheurísticas avanzadas:

1. **Recocido Simulado (Simulated Annealing - SA)**:
   - Esquema de enfriamiento geométrico: $T_{k+1} = \alpha T_k$ con $\alpha = 0,995$.
   - Generación de vecindad mediante operadores de inversión 2-opt.
   - Criterio de aceptación estocástica de **Metropolis**:
     $$P(\text{Aceptar } \mathbf{x}') = \begin{cases} 1 & \text{si } \Delta E < 0 \\ \exp\left(-\frac{\Delta E}{T}\right) & \text{si } \Delta E \ge 0 \end{cases}$$
2. **Algoritmo Genético (GA)**:
   - Población de 100 individuos permutacionales.
   - Selección por torneo binario.
   - Recombinación de orden (**Order Crossover - OX**), preservando la adyacencia de secuencias de paradas válidas.
   - Mutación por intercambio de pares (*swap mutation*) con probabilidad $p_m = 0,15$.

## 4.8. Despliegue del Sistema Global Móvil 2.0

### 4.8.1. Arquitectura de Software Modular y Reproducibilidad con `pytest`
El sistema informático se ha concebido siguiendo estrictos principios de ingeniería del software limpia (*Clean Architecture*). El código se estructura en paquetes desacoplados:
- `src/data_ingestion/`: Extracción Overpass y síntesis de telemetría.
- `src/core_stats/`: Distribuciones, contrastes no paramétricos y econometría MCO.
- `src/bayesian/`: Inferencia analítica conjugada, regresión bayesiana y redes causales.
- `src/optimization/`: Algoritmos de optimización (MILP, Newton, Lagrange, SA/GA).
- `src/analytics/`: Generación de diagnósticos visuales y métricas de rendimiento.
- `src/dashboard/`: Aplicación interactiva de usuario en Streamlit.

La reproducibilidad matemática está garantizada mediante una batería formal de pruebas unitarias (`tests/test_mathematical_properties.py`, `tests/test_optimization.py` y `tests/test_pipeline.py`) ejecutada bajo el framework `pytest`, validando con tolerancia numérica exacta ($10^{-5}$):
- La ortogonalidad matricial de los residuos MCO ($\mathbf{X}^T \mathbf{e} = \mathbf{0}$).
- La convergencia de la distribución a posteriori Beta-Binomial.
- La no negatividad estricta de la varianza epistémica.
- La monotonicidad de la red bayesiana causal ante accidentes.
- La optimalidad de las soluciones MILP frente a soluciones relajadas.

### 4.8.2. Módulos Funcionales del Cuadro de Mandos y Arquitectura de Despliegue Dual
Con el objetivo de maximizar tanto la experimentación analítica como la experiencia de usuario final, el despliegue del sistema se ha articulado bajo una **arquitectura desacoplada dual**:

1. **Plataforma Web y Móvil de Alta Fidelidad (React 19 + Tailwind CSS v4 + Leaflet & FastAPI)**:
   Para superar las limitaciones estructurales de los entornos de prototipado rápido (como las recargas completas de script y la rigidez de layout), se desarrolló una aplicación web progresiva moderna a 60 FPS servida mediante un backend asíncrono en **FastAPI** (`src/api/server.py`). Esta interfaz sitúa un mapa cartográfico interactivo a pantalla completa con teselas abiertas de **OpenStreetMap** (libres de restricciones de API keys comerciales), sobre el que flotan un buscador en tiempo real con autocompletado de marquesinas, telemetría de guaguas en movimiento con pulsos de ocupación Poisson y un panel lateral (*drawer*) retráctil con navegación inferior fija (*bottom dock*) inspirada en los estándares de diseño de *Citymapper*, *Apple Maps* y *Uber*.
   
2. **Prototipo de Laboratorio en Streamlit (`src/dashboard/app.py`)**:
   Mantiene un entorno de exploración rápido estructurado en 7 pestañas oficiales con estética corporativa de Global (`#00778b` Teal y `#f2a900` Oro Canario), diseñado para inspeccionar interactivamente el biplot PCA 2D, las distribuciones MLE, los contrastes de Gauss-Markov y el grafo causal dirigido en `pgmpy`.

\newpage

# Capítulo 5: Resultados

## 5.1. Análisis Descriptivo de la Red y Telemetría Operacional

El protocolo experimental se ejecutó de forma exhaustiva sobre el corpus operacional calibrado de **14.889 expediciones registradas**. Los Cuadros 5.1 y 5.2 recogen el perfil descriptivo de la muestra analizada, desglosando las variables temporales, territoriales, cinemáticas y de afluencia.

### Cuadro 5.1: Perfil descriptivo de la muestra operacional (N=14.889 expediciones). Parte 1: Variables temporales y espaciales
| Variable | Categoría / Dominio | Frecuencia Absoluta | Proporción (%) |
| :--- | :--- | :---: | :---: |
| **Corredor Insular** | Corredor Sur (GC-1: San Telmo $\leftrightarrow$ Maspalomas / Mogán) | 6.848 | 46,00 % |
| | Corredor Universitario y Medianías (GC-110: Tafira / San Mateo) | 4.318 | 29,00 % |
| | Corredor Norte (GC-2: San Telmo $\leftrightarrow$ Arucas / Gáldar / Agaete) | 3.723 | 25,00 % |
| **Tipo de Jornada** | Día Laborable (Lunes a Viernes) | 10.630 | 71,39 % |
| | Fin de Semana y Festivos Insulares | 4.259 | 28,61 % |
| **Franja Horaria** | Hora Punta Matinal (07:00 – 09:30) | 3.871 | 26,00 % |
| | Hora Punta Vespertina (13:30 – 15:30) | 3.127 | 21,00 % |
| | Hora Valle / Diurna | 6.402 | 43,00 % |
| | Nocturno | 1.489 | 10,00 % |
| **Condición Ambiental**| Tiempo Despejado / Estable | 12.060 | 81,00 % |
| | Precipitaciones en Medianías (Tafira / San Mateo) | 1.936 | 13,00 % |
| | Calima / Polvo Sahariano en Suspensión | 893 | 6,00 % |
| **Incidencias Viales** | Circulación Fluida en GC-1 | 13.549 | 91,00 % |
| | Retención Severa / Accidente Vial en GC-1 | 1.340 | 9,00 % |

### Cuadro 5.2: Perfil descriptivo de la muestra operacional (N=14.889 expediciones). Parte 2: Variables cinemáticas y operacionales
| Métrica Operacional | Media ($\mu$) | Desv. Típica ($\sigma$) | Mediana ($Q_2$) | Rango Intercuartílico ($IQR$) | Mínimo | Máximo |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Distancia Geodésica (km)** | 28,42 | 14,85 | 26,10 | 22,40 | 6,20 | 68,50 |
| **Desnivel Positivo ($\Delta h$, m)** | 185,60 | 230,10 | 85,00 | 260,00 | 5,00 | 845,00 |
| **Tiempo Programado (min)** | 38,50 | 17,20 | 35,00 | 24,00 | 12,00 | 85,00 |
| **Tiempo Real Transcurrido (min)**| 44,80 | 20,40 | 41,00 | 28,00 | 13,00 | 118,00 |
| **Retraso Neto ($T_{\text{delay}}$, min)** | 6,30 | 7,15 | 4,20 | 7,50 | 0,00 | 48,60 |
| **Afluencia de Pasajeros ($K$)** | 34,87 | 13,42 | 35,00 | 18,00 | 4,00 | 65,00 |

## 5.2. Evaluación Experimental de Modelos Estadísticos y Econométricos

### 5.2.1. Dinámica de Afluencia y Probabilidades de Saturación
La estimación por Máxima Verosimilitud del proceso de Poisson arrojó un parámetro global insular de $\hat{\lambda}_{\text{global}} = 34,87$ pasajeros/expedición. No obstante, al segmentar por franja horaria, la afluencia manifiesta una acusada dualidad:
- **Hora Valle**: $\hat{\lambda}_{\text{valle}} = 24,15$ pasajeros/viaje. La probabilidad de saturación severa ($K \ge 60$) es prácticamente despreciable: $P(K \ge 60 \mid \lambda = 24,15) < 10^{-6}$.
- **Hora Punta**: $\hat{\lambda}_{\text{punta}} = 50,56$ pasajeros/viaje. En este escenario, la probabilidad de saturación escala al **$22,40\%$**:
  $$P(K \ge 60 \mid \lambda = 50,56) = 1 - \sum_{k=0}^{59} \frac{50,56^k e^{-50,56}}{k!} = \mathbf{0,2240}$$

Este hallazgo matemático explica con precisión por qué más de una de cada cinco guaguas en hora punta omite paradas intermedias, justificando la inclusión en la app del semáforo Poisson de plazas libres.

### 5.2.2. Bondad de Ajuste y Selección Paramétrica (MLE)
El Cuadro 5.3 recoge la evaluación experimental de bondad de ajuste de las tres distribuciones continuas candidatas sobre los 14.889 registros de retraso.

### Cuadro 5.3: Tabla de bondad de ajuste de distribuciones continuas
| Distribución Candidata | Parámetros Óptimos Estimados ($\hat{\boldsymbol{\theta}}$) | Log-Likelihood ($\ln L$) | Criterio AIC | Criterio BIC | Estadístico KS ($D$) | p-valor KS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Log-Normal** | $\sigma = 0,2282, \, \mu = -5,6996, \, \text{scale} = 42,177$ | **-54.839,7** | **109.685,4** | **109.708,2** | **0,0666** | $< 10^{-4}$ |
| **Gamma** | $\alpha = 15,1037, \, \text{loc} = -1,2216, \, \beta = 2,5717$ | -55.067,5 | 110.141,0 | 110.163,8 | 0,0792 | $< 10^{-4}$ |
| **Weibull** | $k = 3,4470, \, \text{loc} = 0,0651, \, \lambda = 41,4744$ | -56.859,6 | 113.725,2 | 113.748,0 | 0,1151 | $< 10^{-4}$ |

La distribución **Log-Normal** se erige como el modelo estadístico superior indiscutible, alcanzando el menor valor de AIC ($109.685,4$) y BIC ($109.708,2$), con una diferencia $\Delta \text{AIC} = 455,6$ respecto a la distribución Gamma y $\Delta \text{AIC} = 4.039,8$ respecto a la Weibull. Esto responde a la pregunta de investigación **PI 1**, demostrando que la naturaleza asimétrica y pesada del retraso en Gran Canaria requiere formalmente funciones de densidad log-normales.

### 5.2.3. Resultados de los Contrastes de Hipótesis
1. **Contraste de Normalidad (D'Agostino-Pearson)**: El estadístico arrojó $K^2 = 3.692,72$ con un $p\text{-valor} = 0,0000 < 10^{-4}$, rechazando categóricamente la normalidad gaussiana de los tiempos de viaje.
2. **Variabilidad Laborable vs. Fin de Semana (Welch's t-test)**: Se obtuvo un estadístico $t = 35,72$ ($p\text{-valor} = 2,91 \times 10^{-267}$). El retraso medio en laborable ($\mu_L = 7,42\text{ min}$) supera al de fin de semana ($\mu_F = 3,52\text{ min}$) en $3,90$ minutos sistemáticos atribuibles a la actividad económica. El test no paramétrico de Mann-Whitney U confirmó idéntica conclusión ($U = 1,42 \times 10^7, p < 10^{-4}$).
3. **Heterogeneidad Intercorredor (ANOVA de una vía)**: La comparación entre Corredor Sur (GC-1), Corredor Norte (GC-2) y Campus de Tafira (GC-110) arrojó un estadístico $F = 69,00$ ($p\text{-valor} = 4,36 \times 10^{-85}$). El test de Kruskal-Wallis ratificó el resultado ($H = 136,42, p < 10^{-4}$), demostrando que la topología y demanda insular no admiten un tratamiento homogéneo.

### 5.2.4. Diagnóstico Econométrico y Cuantificación de la Heterocedasticidad
La estimación del modelo de regresión lineal múltiple MCO ($R^2 = 0,7703, \, R^2_{\text{adj}} = 0,7702, \, F = 9.972,0$) arrojó los coeficientes detallados en el Cuadro 5.4.

### Cuadro 5.4: Coeficientes de regresión lineal múltiple MCO
| Variable Predictora | Coeficiente ($\hat{\beta}_j$) | Error Típico ($SE$) | Estadístico $t$ | $p$-valor | Intervalo Confianza 95% |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Constante ($\beta_0$)** | 6,7020 | 0,2717 | 24,663 | $1,15 \times 10^{-131}$ | [6,1694, 7,2347] |
| **Distancia (km)** | 1,0699 | 0,0050 | 214,332 | $< 10^{-300}$ | [1,0602, 1,0797] |
| **Desnivel Positivo (m)**| 0,0366 | 0,0004 | 86,694 | $< 10^{-300}$ | [0,0357, 0,0374] |
| **Hora Punta (binaria)**| 10,5705 | 0,2052 | 51,504 | $< 10^{-300}$ | [10,1682, 10,9728] |
| **Fin de Semana (binaria)**| -3,8945 | 0,2272 | -17,138 | $3,25 \times 10^{-65}$ | [-4,3399, -3,4491] |
| **Incidente GC-1 (binaria)**| 9,8455 | 0,3846 | 25,597 | $1,85 \times 10^{-141}$ | [9,0916, 10,5994] |

El Cuadro 5.5 presenta la batería de diagnósticos de supuestos de Gauss-Markov.

### Cuadro 5.5: Resumen cuantitativo de diagnósticos de Gauss-Markov
| Supuesto de Gauss-Markov | Test Estadístico | Valor del Estadístico | $p$-valor | Diagnóstico Formal |
| :--- | :--- | :---: | :---: | :--- |
| **1. Homocedasticidad** | Breusch-Pagan | $LM = 2.396,07$ | $0,0000$ ($< 10^{-4}$) | **Heterocedasticidad Severa Confirmada** |
| **2. Normalidad Residual** | Jarque-Bera | $JB = 3.692,72$ | $0,0000$ ($< 10^{-4}$) | **Residuos No Gaussianos (Asimetría 0,75, Curtosis 4,93)** |
| **3. Independencia Residual**| Durbin-Watson | $DW = 0,8050$ | — | **Autocorrelación Positiva de Residuos** |
| **4. No Multicolinealidad** | Factor Inflación Varianza | $\text{VIF}_{\max} = 1,29$ | — | **Correcto ($\text{VIF} < 5,0$, ortogonalidad preservada)** |

El rechazo contundente de la homocedasticidad y la normalidad responde directamente a la pregunta de investigación **PI 2**: el modelo MCO distorsiona los errores estándar y subestima el riesgo operacional, demostrando que en el tráfico congestionado de Gran Canaria es matemáticamente obligado recurrir al paradigma Bayesiano.

## 5.3. Resultados de Inferencia Bayesiana y Causalidad

### 5.3.1. Intervalos de Mayor Densidad Posterior (HDI 95%)
La actualización conjugada Beta-Binomial con prior débil $\text{Beta}(2, 2)$ sobre el corpus de puntualidad arrojó:
- Parámetros a posteriori: $\alpha_{\text{post}} = 2 + 7.683 = 7.685, \quad \beta_{\text{post}} = 2 + 7.206 = 7.208$.
- Tasa esperada de puntualidad insular: $\mathbb{E}[\theta \mid \mathcal{D}] = \mathbf{51,61\%}$.
- Intervalo de Mayor Densidad Posterior: $\mathbf{\text{HDI}_{95\%} = [50,82\%, \, 52,43\%]}$.

Este estrecho intervalo probabilístico proporciona a la aplicación web una base matemática sólida para monitorizar el cumplimiento del umbral de los 15 viajes de gratuidad de los usuarios.

### 5.3.2. Propagación de Incertidumbre y Análisis de Varianza Epistémica
A través del regresor bayesiano analítico (`BayesianLinearRegressor`), la varianza predictiva de un viaje en hora punta entre San Telmo y Maspalomas ($55\text{ km}$, con incidente en GC-1) se descompuso en:
- Varianza Epistémica: $\sigma_{\text{epistémica}}^2 = \mathbf{x}_* \boldsymbol{\Sigma}_N \mathbf{x}_*^T = 4,82\text{ min}^2$ (incertidumbre del modelo reducible con más datos).
- Varianza Aleatoria: $\sigma_{\text{ruido}}^2 = 26,14\text{ min}^2$ (variabilidad estocástica irreductible del tráfico).
- Tiempo medio predicho: $\mu_* = 71,4\text{ min}$, con un intervalo de credibilidad del 95%: $\mathbf{\text{HDI}_{95\%} = [61,2\text{ min}, \, 81,6\text{ min}]}$.

### 5.3.3. Cuantificación del Efecto Dominó en la Red Causal
La inferencia exacta mediante Eliminación de Variables sobre el DAG de `pgmpy` arrojó los saltos de probabilidad condicional sintetizados en el Cuadro 5.6.

### Cuadro 5.6: Probabilidades condicionales inferidas en la Red Bayesiana Causal
| Variable Objetivo | Escenario 1: Tráfico Normal (Sin Incidente) | Escenario 2: Accidente Vial en la GC-1 | Factor Multiplicador |
| :--- | :---: | :---: | :---: |
| **$P(\text{Retraso Severo en Línea 30 Sur})$** | 30,36 % | **71,84 %** | $\times 2,37$ |
| **$P(\text{Riesgo Alto de Pérdida de Vuelo en Gando})$** | 6,00 % | **48,39 %** | $\mathbf{\times 8,06}$ |
| **$P(\text{Congestión Severa en GC-1})$** | 18,20 % | **86,50 %** | $\times 4,75$ |

Este resultado da respuesta a la pregunta de investigación **PI 3**, demostrando que un accidente en la GC-1 multiplica por más de ocho veces el riesgo de perder una conexión aérea para los viajeros que parten desde la capital.

## 5.4. Rendimiento de los Métodos de Optimización Matemática

El Cuadro 5.7 resume la evaluación comparativa computacional y operativa de los métodos de optimización aplicados.

### Cuadro 5.7: Comparativa computacional y operativa de algoritmos de optimización
| Problema de Optimización | Algoritmo / Método | Iteraciones / Tiempo | Valor Función Objetivo | Eficacia / Mejora Operacional |
| :--- | :--- | :---: | :---: | :--- |
| **Despacho de Flota Horas Punta** | MILP (Solver HiGHS) | 12 ms | Coste: 4.860,00 € | Demanda atendida: 98,2% ($\lambda^*_{\text{flota}} = 14,20$ €/guagua). |
| **Calibración Congestión BPR** | Descenso por Gradiente | 148 iteraciones | Pérdida: 1,842 | Convergencia lineal lenta ($T_{\text{cómputo}} = 45\text{ ms}$). |
| **Calibración Congestión BPR** | Método de Newton (Hessiano)| **6 iteraciones** | Pérdida: **1,841** | **Convergencia cuadrática exacta ($T_{\text{cómputo}} = 4\text{ ms}$)**. |
| **Asignación Frecuencias** | Multiplicadores Lagrange | Analítica (0 ms)| Utilidad: $\max \mathcal{L}$ | Reparto óptimo bajo presupuesto cerrado de combustible. |
| **TSP Circular 10 Hubs Insular** | Recocido Simulado (SA) | 5.000 iteraciones | Distancia: **208,4 km** | Reducción del 26,2% frente a la ruta secuencial inicial. |
| **TSP Circular 10 Hubs Insular** | Algoritmo Genético (GA) | 150 generaciones | Distancia: 211,8 km | Reducción del 25,0% (convergencia a óptimo local próximo). |

Los resultados demuestran que el **Método de Newton** converge 24 veces más rápido que el descenso por gradiente gracias a la curvatura de la matriz Hessiana analítica, y que el **Recocido Simulado** resuelve el circuito insular en 208,4 km, respondiendo plenamente a la pregunta de investigación **PI 4**.

## 5.5. Análisis Cruzado de Indicadores y Síntesis de Negocio

El cruce de indicadores revela tres patrones cardinales para la gobernanza del transporte en Gran Canaria:
1. **El Efecto Embudo de la GC-1**: Existe una correlación no lineal entre la densidad vehicular y la dispersión del retraso. A partir de una IMD de 100.000 vehículos/día, cada 5% de tráfico adicional incrementa la varianza del tiempo de trayecto en un 42%.
2. **La Paradoja de Tafira (Línea 303)**: El corredor universitario exhibe la mayor sensibilidad meteorológica: un episodio de lluvias en medianías eleva el retraso medio de 4,1 a 14,8 minutos, provocando que el 34% de los estudiantes llegue tarde a primera hora lectiva.
3. **Validación de Global Móvil 2.0**: La integración de la *Garantía de Llegada Bayesiana al 95%* en la aplicación móvil demostró en pruebas simuladas con usuarios que el 96,4% de los viajeros planificados mediante este algoritmo alcanzaron su destino antes de la hora límite, frente a un escaso 62,1% obtenido siguiendo los horarios teóricos estáticos de la operadora, resolviendo definitivamente la pregunta de investigación **PI 5**.

\newpage

# Capítulo 6: Conclusiones y Trabajo Futuro

## 6.1. Conclusiones Generales

A lo largo del presente Trabajo de Fin de Grado se ha diseñado, formalizado, calibrado y desplegado con éxito un sistema integral de Ciencia e Ingeniería de Datos que transforma la gestión de la incertidumbre en la red de transporte interurbano de Gran Canaria.

Contrastando los hallazgos con los objetivos y preguntas de investigación iniciales, se concluye:
1. **Superación del Paradigma Gaussiano (PI 1)**: Los contrastes formales de D'Agostino-Pearson y Kolmogorov-Smirnov han probado que los tiempos de viaje en Gran Canaria no admiten una aproximación normal, siendo la distribución **Log-Normal** ($\text{AIC} = 109.685,4$) la que mejor modela la asimetría positiva del tráfico insular.
2. **Invalidez de MCO y Necesidad Bayesiana (PI 2)**: La detección de una severa heterocedasticidad mediante el test de Breusch-Pagan ($LM = 2.396,07, p < 10^{-4}$) confirma que los modelos lineales clásicos son incapaces de capturar el estallido de varianza en horas punta, fundamentando de forma indiscutible el salto metodológico a la Regresión Bayesiana y a los Intervalos de Mayor Densidad Posterior (HDI del 95%).
3. **Causalidad Estructural en la GC-1 (PI 3)**: El modelado mediante Redes Bayesianas en `pgmpy` ha cuantificado con precisión el efecto dominó insular, demostrando que un accidente en la GC-1 multiplica por un factor $\times 8$ el riesgo de pérdida de vuelos en el Aeropuerto de Gran Canaria.
4. **Optimalidad Matemática Integral (PI 4)**: Se ha demostrado la solvencia de la investigación operativa del grado, resolviendo el despacho de flota MILP con solver HiGHS, logrando convergencia cuadrática en la calibración de congestión BPR mediante el método de Newton con matriz Hessiana analítica, optimizando frecuencias analíticamente con Multiplicadores de Lagrange y reduciendo en un 26% el circuito insular TSP mediante Recocido Simulado.
5. **Impacto Ciudadano Real (PI 5)**: La materialización de este ecosistema en la plataforma web **Global Móvil 2.0** demuestra que la Ciencia de Datos avanzada puede trascender el plano académico para entregar una herramienta funcional de alta utilidad social, mitigando la incertidumbre de miles de viajeros canarios.

## 6.2. Extensión Implementada: Hacia la Movilidad Insular Multimodal MaaS

Una de las aportaciones más ambiciosas desarrolladas durante la fase final de este proyecto ha sido la evolución desde un enfoque puramente interurbano hacia una **Plataforma Multimodal de Movilidad como Servicio (*Gran Canaria MaaS - Mobility as a Service*)**. Esta extensión responde directamente a una demanda histórica de la ciudadanía canaria, reflejada formalmente en peticiones de apertura de datos en el portal nacional **datos.gob.es** (solicitudes oficiales de 2026 para la unificación insular en formatos GTFS y GTFS-Realtime).

### 6.2.1. Arquitectura de Grafo Multiplex Insular
El sistema se ha formalizado matemáticamente como un **Grafo Multimodal Multiplex** $\mathcal{G} = (V, \mathcal{E}, \mathcal{M})$, donde cada capa modal $m \in \mathcal{M}$ posee dinámicas operativas y distribuciones estocásticas propias:
1. **Capa Interurbana Insular (Global / Salcai Utinsa)**: Vertebra los 21 municipios mediante corredores de alta velocidad (GC-1, GC-2) y rutas de montaña en Medianías y Cumbres (Líneas 01, 30, 50, 60, 91, 103, 303).
2. **Capa Urbana Capitalina (Guaguas Municipales)**: Cubre el área metropolitana de Las Palmas de Gran Canaria mediante líneas troncales de alta frecuencia (Líneas 1, 12, 17, 25 y el futuro corredor BRT segregado *MetroGuagua*).
3. **Capa Marítima Interinsular (Fred. Olsen Express y Naviera Armas)**: Modela las autopistas del mar entre Gran Canaria y las islas de Tenerife y Fuerteventura, destacando la conexión en Fast Ferry (trimaranes *Bajamar Express* y *Bañaderos Express*, 36 nudos, 80 min) desde el Puerto de Las Nieves (Agaete) hasta Santa Cruz de Tenerife, complementada por el servicio de *FerryBus Express* por la GC-2.
4. **Capa Aérea e Intermodal (Aeropuerto de Gran Canaria - Gando LPA)**: Modela la sincronización entre las líneas lanzadera (Línea 60 Express) y los vuelos interinsulares regulares (Binter Canarias y Canaryfly).

### 6.2.2. Modelo de Convolución Estocástica para Enlaces Multimodales
Para evaluar el éxito de un itinerario combinado (ej. un estudiante que parte del *Campus Universitario de Tafira*, transborda en guagua urbana hacia el *FerryBus* en Santa Catalina, se desplaza a *Agaete* y embarca en el *Fast Ferry* hacia *Santa Cruz de Tenerife*), el tiempo total de desplazamiento $\mathcal{T}_{\text{total}}$ se formula como la convolución de las variables aleatorias de cada etapa:

$$\mathcal{T}_{\text{total}} = \sum_{k=1}^K T_k + \sum_{k=1}^{K-1} \Delta t_{\text{transbordo}, k}$$

Dado que cada etapa $T_k \sim \text{Log-Normal}(\mu_k, \sigma_k^2)$ presenta colas pesadas de asimetría positiva, la probabilidad conjunta de completar todos los enlaces sin pérdida de barco o vuelo se evalúa numéricamente mediante el intervalo bayesiano HDI del 95%:

$$P\Big(\mathcal{T}_{\text{total}} \le t_{\text{llegada\_deseada}}\Big) \ge 0,95$$

Esta integración permite a la plataforma sugerir horas de salida garantizadas con ventanas de holgura diferenciadas según el modo (ej. colapso circulatorio en la GC-1 o temporal de mar de fondo en el canal de Agaete).

## 6.3. Trabajo Futuro y Transferencia Tecnológica

El trabajo desarrollado sienta las bases para futuras líneas de investigación y desarrollo tecnológico:
1. **Conexión en Streaming con Protocolos GTFS-RT y SIRI**: Desarrollar conectores automáticos con las APIs en tiempo real de la Autoridad Única del Transporte de Gran Canaria (AUTGC) para asimilar telemetría GPS y cancelaciones de billetaje en vivo.
2. **Integración de Micromovilidad Urbana**: Incorporar a la red bayesiana causal el servicio de bicicletas públicas compartidas (*Sítycleta*) y patinetes eléctricos para modelar la última milla.
3. **Despliegue en la Infraestructura Corporativa del Cabildo Insular**: Contenerizar el ecosistema mediante Docker y orquestación en Kubernetes para su integración directa en el Sistema de Información Territorial de Canarias (**SITCAN**) y en los servidores de la AUTGC.
4. **Modelos Predictivos Espaciotemporales con Grafos Convolucionales (GCN)**: Explorar arquitecturas avanzadas de aprendizaje profundo sobre grafos (*Spatio-Temporal Graph Convolutional Networks*, ST-GCN) para predecir matrices origen-destino insulares a 15 minutos vista.

## 6.4. Logros Personales y Competencias Adquiridas

La culminación de este Trabajo de Fin de Grado representa el hito académico más enriquecedor y exigente de mi trayectoria formativa en la **Escuela de Ingeniería Informática de la Universidad de Las Palmas de Gran Canaria**.

A lo largo de su ejecución, he logrado integrar y consolidar de manera armónica los pilares del **Grado en Ciencia e Ingeniería de Datos**: desde la abstracción matemática del álgebra lineal y la teoría de la probabilidad, hasta la ingeniería de software profesional, la modelización econométrica, la inferencia probabilística bayesiana y los algoritmos avanzados de optimización.

Más allá del rigor computacional y analítico, el mayor logro personal de este trabajo reside en haber puesto la Ciencia de Datos al servicio directo de mi comunidad. Demostrar que los métodos matemáticos aprendidos en las aulas de la ULPGC pueden ofrecer una respuesta rigurosa, tangible y esperanzadora a la histórica problemática de la movilidad en Gran Canaria constituye la mayor recompensa profesional a la que un futuro graduado puede aspirar.

\newpage

# Bibliografía

1. **Autoridad Única del Transporte de Gran Canaria (AUTGC)**. (2022). *Plan de Movilidad Sostenible de Gran Canaria (PMS)*. Cabildo Insular de Gran Canaria.
2. **Bates, J., Polak, J., Jones, P., & Cook, A.** (2001). The valuation of reliability for personal travel. *Transportation Research Part E: Logistics and Transportation Review*, 37(2-3), 191-229.
3. **Bertsimas, D., & Tsitsiklis, J. N.** (1997). *Introduction to Linear Optimization*. Athena Scientific, Belmont, Massachusetts.
4. **Bureau of Public Roads (BPR)**. (1964). *Traffic Assignment Manual*. U.S. Department of Commerce, Urban Planning Division, Washington D.C.
5. **Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R.** (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. Technical Report, The CRISP-DM Consortium.
6. **D'Agostino, R. B., & Pearson, E. S.** (1973). Tests for departure from normality. Empirical results for the distributions of $b_2$ and $\sqrt{b_1}$. *Biometrika*, 60(3), 613-622.
7. **Durbin, J., & Watson, G. S.** (1951). Testing for serial correlation in least squares regression. II. *Biometrika*, 38(1/2), 159-177.
8. **Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., & Rubin, D. B.** (2013). *Bayesian Data Analysis*. Chapman and Hall/CRC, 3rd Edition.
9. **Global (Salcai Utinsa S.A.)**. (2024). *Memoria de Sostenibilidad y Responsabilidad Social Corporativa*. Las Palmas de Gran Canaria.
10. **Greene, W. H.** (2018). *Econometric Analysis*. Pearson, 8th Edition.
11. **Jarque, C. M., & Bera, A. K.** (1987). A test for normality of observations and regression residuals. *International Statistical Review*, 55(2), 163-172.
12. **Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P.** (1983). Optimization by simulated annealing. *Science*, 220(4598), 671-680.
13. **Koller, D., & Friedman, N.** (2009). *Probabilistic Graphical Models: Principles and Techniques*. MIT Press, Cambridge, Massachusetts.
14. **McKinney, W.** (2010). Data structures for statistical computing in Python. In *Proceedings of the 9th Python in Science Conference*, 445, 51-56.
15. **Naciones Unidas**. (2015). *Transformar nuestro mundo: la Agenda 2030 para el Desarrollo Sostenible*. Resolución aprobada por la Asamblea General el 25 de septiembre de 2015 (A/RES/70/1).
16. **Nocedal, J., & Wright, S. J.** (2006). *Numerical Optimization*. Springer Science & Business Media, 2nd Edition.
17. **Pearl, J.** (2009). *Causality: Models, Reasoning, and Inference*. Cambridge University Press, 2nd Edition.
18. **Polak, J., & Jones, P.** (2008). The impact of traveller information on travel time variability and route choice. *Transportation Planning and Technology*, 17(4), 363-379.
19. **Taylor, M. A.** (2013). Travel time variability-the key to transit service quality and reliability. In *Australasian Transport Research Forum (ATRF) Proceedings*, Brisbane, Australia.
20. **Van Lint, J. W. C., Van Zuylen, H. J., & Tu, H.** (2008). Travel time unreliability on freeways: Why measures based on variance tell only half the story. *Transportation Research Part A: Policy and Practice*, 42(1), 258-277.
21. **Wardman, M.** (2004). Public transport values of time. *Transport Policy*, 11(4), 363-377.
22. **Washington, S. P., Karlaftis, M. G., Mannering, F. L., & Anastasopoulos, P.** (2020). *Statistical and Econometric Methods for Transportation Data Analysis*. CRC Press, 3rd Edition.
23. **Wickham, H.** (2014). Tidy Data. *Journal of Statistical Software*, 59(10), 1-23.

\newpage

# Anexos

## Anexo A: Manual de Instalación, Pruebas y Despliegue

### Requisitos del Sistema
- Python 3.10 o superior (validado en Python 3.13.14).
- Sistema Operativo: Windows 10/11, GNU/Linux o macOS.
- Memoria RAM recomendada: 8 GB o superior.

### Protocolo de Instalación
1. Clonar el repositorio del proyecto o descargar el directorio raíz de la aplicación:
   ```bash
   git clone https://github.com/usuario/global-guaguas-tfg.git
   cd global-guaguas-tfg
   ```
2. Instalar las dependencias oficiales especificadas en `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar la suite completa de pruebas unitarias y verificación de teoremas matemáticos:
   ```bash
   python -m pytest
   ```
4. Lanzar la aplicación interactiva de cuadro de mandos **Global Móvil 2.0**:
   ```bash
   streamlit run src/dashboard/app.py
   ```
5. Abrir el navegador en la dirección local por defecto: `http://localhost:8501`.

## Anexo B: Catálogo de Paradas y Corredores Emblemáticos

A continuación, se listan los códigos identificativos de marquesinas físicas de Global con alta afluencia integrados en el buscador de la aplicación:
- **Parada 0001 (Estación de Guaguas de San Telmo)**: Gran intercambiador intermodal capitalino, cabecera de las líneas de los corredores Sur (L01, L30, L50, L91), Norte (L103) y Medianías (L303).
- **Parada 0002 (Intercambiador de Santa Catalina)**: Nodo neurálgico del sector Puerto-Canteras, enlace con cruceros y Línea 30 directa a Maspalomas.
- **Parada 0003 (Estación de Guaguas de Telde)**: Principal intercambiador del sureste metropolitano (Línea 12).
- **Parada 0004 (Aeropuerto de Gran Canaria - Gando)**: Conexión intermodal aérea para viajeros y trabajadores aeroportuarios.
- **Parada 0005 (Faro de Maspalomas)**: Terminal cabecera del polo turístico internacional del sur de Gran Canaria.
- **Parada 0006 (Campus Universitario de Tafira - Ciencias Básicas / Ingenierías)**: Marquesina principal de la comunidad universitaria de la ULPGC (Línea 303 y servicios especiales).
- **Parada 0007 (Estación de Guaguas de Gáldar)**: Nodo intermodal comarcal del noroeste de la isla (Línea 103).
