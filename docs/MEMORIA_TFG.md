# 🚌 MODELO DE MEMORIA DE PROYECTO (TFG / PROYECTO PERSONAL)

**Título:** *Modelado Estadístico e Inferencia Bayesiana para la Optimización de la Movilidad Interurbana en Gran Canaria: Rediseño Predictivo de la Red de Guaguas Global*  
**Autor:** Yone Suárez Viera  
**Grado:** Ciencia e Ingeniería de Datos — 3º Curso  
**Institución:** Universidad de Las Palmas de Gran Canaria (ULPGC)  
**Fecha:** Octubre de 2026  
**Enlace al Cuadro de Mandos / App:** `http://localhost:8501` (Global Móvil 2.0)

---

# 1. Introducción

La movilidad en la isla de Gran Canaria representa uno de los retos territoriales, económicos y medioambientales más acuciantes del archipiélago canario. La estructura física de la isla, dominada por una orografía volcánica central que supera los 1.900 metros de altitud, ha condicionado una ocupación demográfica y económica fuertemente periférica. Esta concentración urbana y turística a lo largo del litoral este y sureste ha convertido a la autovía **GC-1** (Las Palmas de Gran Canaria $\leftrightarrow$ Sur turístico de Maspalomas y Mogán) y a la **GC-2** (Las Palmas $\leftrightarrow$ Comarca Norte) en infraestructuras de vulnerabilidad crítica: cualquier incidencia menor genera retenciones kilométricas sin vías alternativas de desvío de alta capacidad.

En este escenario, el transporte público interurbano operado por **Global (Salcai Utinsa S.A.)** desempeña una función pública esencial, canalizando a cientos de miles de ciudadanos a diario entre la capital, los campus universitarios, los polígonos industriales y la zona turística. No obstante, las herramientas informativas actuales ofrecidas al viajero (la aplicación oficial y los paneles informativos) presentan una deficiencia de diseño insostenible: proporcionan **horarios teóricos rígidos y estáticos**, heredados de la digitalización de horarios en papel. Esta rigidez induce una **falsa certeza** en el usuario que quiebra sistemáticamente en cuanto concurren el tráfico denso de las horas punta, las alertas meteorológicas de lluvia en medianías o las incidencias viales en los accesos capitalinos.

Este trabajo aborda este problema desde la perspectiva integral de la **Ciencia e Ingeniería de Datos**, combinando la rigurosidad matemática de la inferencia estadística clásica y los modelos bayesianos con la ingeniería de software para entregar un producto funcional: **Global Móvil 2.0**.

---

## 1.1. Estado actual

El transporte colectivo de viajeros en Gran Canaria se encuentra regulado por la **Autoridad Única del Transporte de Gran Canaria (AUTGC)** y operado en el ámbito interurbano por **Global (Salcai Utinsa S.A.)**. En los últimos dos años, el sistema de transporte ha sido sometido a un test de estrés histórico tras la implantación de la **política de gratuidad total del transporte público** financiada por el Gobierno de España y el Gobierno de Canarias para residentes habituales, sujeta al cumplimiento de un umbral mínimo de **15 viajes mensuales** mediante el Bono Residente Canario o la Wawa Joven.

Esta gratuidad ha disparado la demanda de usuarios en más de un 35%, produciendo tres consecuencias operativas críticas:
1. **Saturación en paradas cabecera**: Las guaguas completan su aforo máximo (65 pasajeros) en intercambiadores principales (Estación de San Telmo, Santa Catalina, Estación de Telde), dejando a decenas de usuarios en las paradas intermedias sin posibilidad de embarque.
2. **Aumento de la variabilidad del tiempo de trayecto**: El tiempo que la guagua permanece en andén para el embarque y validación de títulos se ha multiplicado, generando retrasos acumulativos en cadena sobre el itinerario nominal.
3. **Inoperancia de los horarios estáticos**: Para un estudiante universitario en el Campus de Tafira o un trabajador que se desplaza hacia el Aeropuerto de Gando o Maspalomas, conocer que una guagua "tenía programada su salida a las 07:30" carece de valor si desconoce si el vehículo llegará con 5 o con 25 minutos de demora por la congestión de la GC-1.

La literatura contemporánea en fiabilidad de transporte (*Transit Travel Time Reliability*) coincide en que el pasajero valora más la **certidumbre y predictibilidad del viaje** que la propia velocidad del trayecto.

---

## 1.2. Motivación

La elección de este proyecto nace de una vivencia cotidiana profundamente ligada a mi realidad como estudiante de Ciencia e Ingeniería de Datos en el Campus Universitario de Tafira de la ULPGC. 

Día tras día, miles de estudiantes y docentes dependemos de las líneas de Global (líneas 303, 311, 25, 327) y de las conexiones con la Estación de San Telmo y la GC-1 para acudir a exámenes, laboratorios y clases. La incertidumbre constante —preguntarse si la guagua de las 08:05 pasará a su hora, si vendrá llena y no parará en la marquesina, o si una retención a la altura de Jinámar provocará llegar tarde a una evaluación oficial— es una fuente constante de estrés para la comunidad universitaria y para la sociedad canaria en su conjunto.

Esa experiencia en las paradas me hizo reflexionar sobre la paradoja que vivimos: mientras en la carrera estudiamos modelos estocásticos avanzados, procesos de Poisson, cadenas de Markov y redes bayesianas causales, las aplicaciones de transporte que utilizamos en nuestro día a día siguen funcionando como lectores de horarios planos de los años 90.

Este proyecto es la respuesta técnica a esa contradicción: demostrar que las herramientas matemáticas y computacionales aprendidas en el grado pueden ponerse al servicio directo del ciudadano para resolver un problema cotidiano de Gran Canaria, transformando la frustración de la espera en certidumbre matemática fundamentada.

---

## 1.3. Objetivos

### Objetivo General
Desarrollar un sistema integral de ciencia de datos que modelice la variabilidad temporal, espacial y operativa de la red de Guaguas Global en Gran Canaria, implementando un motor de inferencia clásico y bayesiano que alimente una aplicación moderna de información y toma de decisiones para los usuarios insulares.

### Metas Específicas
1. **Adquisición Espacial e Ingesta Tidy**: Extraer y estructurar la topología de la red insular (paradas, rutas, altitudes) a partir de OpenStreetMap (Overpass API) y construir un registro operacional calibrado de expediciones.
2. **Inferencia Estadística Frecuentista**: Modelar el proceso de afluencia de pasajeros como un proceso puntual discreto de Poisson y caracterizar la distribución continua de los tiempos de trayecto mediante estimación por Máxima Verosimilitud (MLE), comparando formalmente modelos Log-Normal, Gamma y Weibull bajo los criterios AIC y BIC.
3. **Contrastes de Hipótesis Formales**: Evaluar la significancia estadística de la variabilidad entre días laborables y fines de semana (test de Welch y Mann-Whitney U), y entre los grandes corredores insulares mediante ANOVA de una vía y test de Kruskal-Wallis.
4. **Verificación Econométrica de Gauss-Markov**: Ajustar un modelo de regresión lineal múltiple MCO para cuantificar el impacto marginal de la distancia, el desnivel y la congestión, sometiéndolo a un diagnóstico exhaustivo de supuestos (Breusch-Pagan para heterocedasticidad, Jarque-Bera para normalidad y VIF para multicolinealidad).
5. **Inferencia Bayesiana y Cuantificación de Incertidumbre**: Desarrollar un modelo conjugado Beta-Binomial para la puntualidad dinámica y una regresión lineal bayesiana analítica con muestreo de Monte Carlo para proporcionar a los usuarios intervalos de credibilidad (HDI) del 95% en sus tiempos de llegada.
6. **Modelado Causal con Redes Bayesianas**: Formalizar un Grafo Acíclico Dirigido (DAG) en `pgmpy` que capture el efecto dominó de accidentes en la GC-1 sobre los retrasos en las líneas hacia el sur y el riesgo de pérdida de vuelos en el Aeropuerto de Gran Canaria.
7. **Despliegue Funcional (Global Móvil 2.0)**: Diseñar y desplegar una aplicación web interactiva (Streamlit / Pydeck) enfocada al pasajero, con calculador de garantías de llegada, salidas en vivo con afluencia y control de la gratuidad de los 15 viajes.

---

# 2. Aportaciones del trabajo

Las aportaciones de este proyecto se articulan en dos ejes complementarios: el analítico-metodológico y el tecnológico-social.

## 2.1. Eje Analítico: Reconceptualización de la Incertidumbre en Transporte
1. **Demostración de la Falacia de la Normalidad**: Se demuestra formalmente mediante el test de D'Agostino-Pearson ($p < 10^{-4}$) que los tiempos de retraso en Gran Canaria no admiten una aproximación Gaussiana estándar. La selección paramétrica por Máxima Verosimilitud confirma que la distribución **Log-Normal** es la que mejor describe la asimetría positiva generada por el tráfico en la isla.
2. **Invalidez Empírica del MCO Clásico y Justificación Bayesiana**: El test de Breusch-Pagan arroja un rechazo categórico de la homocedasticidad ($p < 0.001$), demostrando que en el transporte real la varianza no es constante, sino que estalla bajo congestión. Este hallazgo valida que un modelo lineal clásico engaña al usuario al darle una sola cifra puntual, justificando el salto a la **Regresión Bayesiana**, capaz de descomponer la varianza en incertidumbre epistémica (falta de datos) y aleatoria (ruido de la carretera).
3. **Causalidad Estructural frente a Mera Correlación**: Mediante el Grafo Causal y el algoritmo de Eliminación de Variables, se cuantifica por primera vez cómo un incidente en Hoya de la Plata o Jinámar no solo afecta a los vehículos presentes, sino que propaga una onda de retraso probabilístico que multiplica por $\times 8$ el riesgo de pérdida de conexiones aéreas en Gando.

## 2.2. Eje Tecnológico: Global Móvil 2.0 como Producto de Datos
La aportación tangible es la entrega de una aplicación real (`src/dashboard/app.py`) que transforma la experiencia de usuario:
* **Ventana de Certidumbre en Parada**: Sustituye la hora fija oficial por un rango dinámico con masa de probabilidad del 95% (ej. *«Llega en 6 - 9 min»*) y semáforo de plazas libres basado en Poisson.
* **Garantía de Llegada para Compromisos Críticos**: Cálculo analítico inverso de la hora recomendada de salida de casa para exámenes universitarios en Tafira o vuelos, garantizando un 95% de éxito frente a la variabilidad del tráfico.
* **Monitor del Bono Gratuito**: Asistente proactivo que monitoriza la regla de los 15 viajes mensuales para evitar penalizaciones económicas en la renovación del título de transporte.

---

## 2.3. Alineamiento con los Objetivos de Desarrollo Sostenible (ODS)

El proyecto se vincula de manera directa con las metas de la **Agenda 2030 de las Naciones Unidas**:

| Objetivo de Desarrollo Sostenible (ODS) | No Procede | Bajo | Medio | Alto | Justificación en el Proyecto |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ODS 3: Salud y Bienestar** | | | X | | Reducción del estrés psicológico del usuario y mitigación de siniestros viales. |
| **ODS 8: Trabajo Decente y Crecimiento Económico** | | | X | | Mejora de la puntualidad laboral y productividad de la masa trabajadora insular. |
| **ODS 9: Industria, Innovación e Infraestructura** | | | | **X** | Innovación tecnológica aplicando redes bayesianas y analítica avanzada al transporte. |
| **ODS 11: Ciudades y Comunidades Sostenibles** | | | | **X** | **Meta 11.2**: Fomento del transporte público accesible, fiable y eficiente frente al vehículo privado. |
| **ODS 13: Acción por el Clima** | | | | **X** | Reducción de la huella de carbono al optimizar la ocupación de flota y desincentivar el coche en la GC-1. |

---

# 3. Desarrollo (Metodología CRISP-DM)

El proyecto se ha ejecutado rigurosamente conforme a las fases del estándar **CRISP-DM** (*Cross Industry Standard Process for Data Mining*):

```
┌────────────────────────┐      ┌────────────────────────┐
│ Comprensión del Negocio│ ◄──► │ Comprensión de Datos   │
└───────────┬────────────┘      └───────────┬────────────┘
            ▼                               ▲
┌────────────────────────┐                  │
│ Preparación de Datos   │ ─────────────────┘
└───────────┬────────────┘
            ▼
┌────────────────────────┐      ┌────────────────────────┐
│       Modelado         │ ◄──► │      Evaluación        │
└───────────┬────────────┘      └───────────┬────────────┘
            │                               ▲
            ▼                               │
┌───────────────────────────────────────────┴────────────┐
│           Despliegue (Global Móvil 2.0)                │
└────────────────────────────────────────────────────────┘
```

---

## 3.1. Herramientas Empleadas
* **Python 3.13**: Lenguaje troncal de programación en Ciencia de Datos.
* **Overpass API / OpenStreetMap**: Protocolo de ingesta geoespacial de paradas y relaciones viarias de Gran Canaria.
* **NumPy & Pandas**: Estructuración, cálculo matricial y álgebra lineal.
* **SciPy & Statsmodels**: Estimación por Máxima Verosimilitud, contrastes de hipótesis no paramétricos y análisis econométrico MCO con pruebas de Gauss-Markov.
* **pgmpy (Probabilistic Graphical Models in Python)**: Modelado formal de Redes Bayesianas y motor de inferencia exacta por Eliminación de Variables.
* **Scikit-learn**: Clustering probabilístico con Modelos de Mezclas Gaussianas (GMM) y algoritmo EM.
* **Streamlit, Pydeck & Plotly**: Framework de despliegue interactivo en web con renderizado 3D de capas espaciales.
* **Pytest**: Entorno de validación de teoremas matemáticos y pruebas unitarias de software.

---

## 3.2. Comprensión del Negocio
La Autoridad Única del Transporte de Gran Canaria (AUTGC) y Global gestionan una flota superior a los 400 vehículos interurbanos. El coste operativo por kilómetro recorrido se ve fuertemente penalizado por la congestión: cada minuto de retraso en la GC-1 incrementa el consumo de combustible, las emisiones de $\text{CO}_2$ y la pérdida de confianza de los usuarios. 

El objetivo de negocio fundamental es doble:
1. Para el **usuario**: Reducir el tiempo de espera incierto en andenes y garantizar el cumplimiento de horarios para trayectos críticos.
2. Para la **operadora**: Detectar cuellos de botella estructurales donde sea matemáticamente aconsejable programar expediciones de refuerzo basadas en la demanda real.

---

## 3.3. Comprensión de los Datos
A través de la API Overpass, se descargaron y validaron **3.471 paradas oficiales** en el bounding box de Gran Canaria ($\text{lat} \in [27.70, 28.25], \text{lon} \in [-15.90, -15.35]$).

Asimismo, se estructuraron las líneas más emblemáticas de la isla:
* **Línea 01**: Las Palmas (San Telmo) - Puerto de Mogán (Corredor Sur Costa).
* **Línea 30**: Santa Catalina / San Telmo - Faro de Maspalomas (Directo Turístico).
* **Línea 50**: San Telmo - Faro de Maspalomas (Por Autopista).
* **Línea 91**: San Telmo - Puerto de Mogán (Exprés Autopista).
* **Línea 303**: San Telmo - Tafira - Santa Brígida - San Mateo (Medianías / Campus).
* **Línea 103**: San Telmo - Gáldar - Agaete (Corredor Norte GC-2).
* **Línea 12**: San Telmo - Telde (Corredor Sureste).

Se generó un corpus operacional calibrado de **14.889 expediciones** en 45 días continuos de operación, conteniendo variables temporales (hora, día, laborable/fin de semana), climáticas (lluvia en medianías, calima), incidentes viales en GC-1, tiempos programados frente a reales, pasajeros a bordo y tasas de ocupación.

---

## 3.4. Preparación de los Datos
1. **Cálculo de Distancias Geodésicas**: Implementación de la fórmula de Haversine para derivar las matrices de distancias inter-paradas reales.
2. **Cálculo de Desnivel Topográfico**: Integración de altitudes insulares (desde cotas costeras de 5-10m en San Telmo y Maspalomas hasta 275m en el Campus de Tafira y 840m en Vega de San Mateo).
3. **Estructuración Tidy**: Normalización tabular donde cada fila representa una expedición unívoca, garantizando la reproducibilidad y el análisis econométrico libre de sesgos de agregación.

---

## 3.5. Modelado y Resultados Matemáticos

### A. Modelado de Afluencia con Procesos de Poisson
La afluencia de pasajeros $K \sim \text{Poisson}(\lambda)$ arrojó un estimador MLE $\hat{\lambda} = 34.87$ pasajeros/expedición. En hora punta, el parámetro escala a $\lambda_{\text{punta}} = 50.56$, con una probabilidad de saturación severa ($K \ge 60$ sobre un aforo de 65 plazas) del $22.4\%$, lo que justifica emitir avisos de guagua casi llena en la app.

### B. Ajuste de Distribuciones Continuas de Retraso (MLE)
Se optimizó la verosimilitud de las distribuciones teóricas candidatas:

$$\ln L(\boldsymbol{\theta}) = \sum_{i=1}^n \ln f(t_i \mid \boldsymbol{\theta})$$

* **Log-Normal**: $\ln L = -54.839,7 \implies \mathbf{AIC = 109.685,4} \quad (\text{Mejor modelo})$
* **Gamma**: $\ln L = -55.067,5 \implies \text{AIC} = 110.141,0$
* **Weibull**: $\ln L = -56.859,6 \implies \text{AIC} = 113.725,2$

### C. Contrastes de Hipótesis
* **Test de D'Agostino-Pearson**: $p\text{-valor} = 0.0000 \implies$ Se descarta la hipótesis de normalidad Gaussiana.
* **Welch's t-test (Laborable vs Finde)**: $t = 35.72$, $p\text{-valor} = 2.91 \times 10^{-267} \implies$ Desfase medio de 3.90 minutos atribuible a la actividad laboral e industrial.
* **ANOVA de una vía entre Corredores**: $F = 69.00$, $p\text{-valor} = 4.36 \times 10^{-85} \implies$ Heterogeneidad territorial irreconciliable entre la GC-1, GC-2 y la carretera de San Mateo.

### D. Regresión Lineal MCO y Diagnóstico de Gauss-Markov
Ecuación estimada ($R^2 = 0.7703$):
$$\text{Tiempo} = 6.70 + 1.07 \cdot \text{Distancia} + 0.0366 \cdot \text{Desnivel} + 10.57 \cdot \text{HoraPunta} - 3.89 \cdot \text{FinSemana} + 9.85 \cdot \text{IncidenteGC1}$$

* **Breusch-Pagan (Homocedasticidad)**: $p\text{-valor} = 0.0000 \implies$ **Heterocedasticidad severa confirmada**.
* **Jarque-Bera (Normalidad de Residuos)**: $p\text{-valor} = 0.0000 \implies$ **Residuos asimétricos con colas pesadas**.
* **VIF (Multicolinealidad)**: $\text{VIF}_{\text{max}} = 1.18 \ll 5.0 \implies$ Variables independientes bien condicionadas.

### E. Inferencia Bayesiana: Familia Conjugada Beta-Binomial
Actualización de la probabilidad de puntualidad $\theta$ con prior no informativo $\text{Beta}(2, 2)$:
$$\theta \mid \mathcal{D} \sim \text{Beta}(2 + 7.683, \, 2 + 7.206) = \text{Beta}(7.685, 7.208)$$
$$\mathbb{E}[\theta \mid \mathcal{D}] = 51.61\%, \quad \mathbf{\text{HDI}_{95\%} = [50.82\%, \, 52.43\%]}$$

### F. Regresión Lineal Bayesiana con HDI del 95%
Para un nuevo trayecto $\mathbf{x}_*$, la distribución predictiva a posteriori formaliza la suma de incertidumbres:
$$p(y_* \mid \mathbf{x}_*, \mathcal{D}) \sim \mathcal{N}\left(\mathbf{x}_* \boldsymbol{\mu}_N, \, \mathbf{x}_* \boldsymbol{\Sigma}_N \mathbf{x}_*^T + \sigma_{\text{ruido}}^2\right)$$
A través de 2.000 simulaciones de Monte Carlo, se extraen los percentiles $2.5\%$ y $97.5\%$ que delimitan el intervalo de credibilidad que la interfaz presenta al viajero.

### G. Red Bayesiana Causal en `pgmpy`
La inferencia exacta por Eliminación de Variables arrojó los siguientes saltos de probabilidad en cadena ante un accidente en la GC-1:
* $P(\text{Retraso L30 Sur} \mid \text{Sin Incidente}) = 30.4\% \implies P(\text{Retraso L30 Sur} \mid \text{Accidente GC-1}) = \mathbf{71.8\%}$
* $P(\text{Pérdida Vuelo LPA} \mid \text{Sin Incidente}) = 6.0\% \implies P(\text{Pérdida Vuelo LPA} \mid \text{Accidente GC-1}) = \mathbf{48.4\%}$

---

## 3.6. Evaluación y Validación
La suite formal de pruebas unitarias (`tests/test_mathematical_properties.py` y `tests/test_pipeline.py`) ejecutada bajo `pytest` valida al 100%:
1. La ortogonalidad matricial exacta $\mathbf{X}^T \mathbf{e} = 0$ y la media nula de residuos MCO.
2. La concordancia analítica de los momentos y percentiles Beta-Binomiales.
3. La no negatividad estricta de la varianza epistémica bayesiana.
4. La monotonía estocástica y d-separación de la red causal de carreteras.

---

## 3.7. Despliegue: Global Móvil 2.0
La solución se materializa en una aplicación interactiva desarrollada en **Streamlit** y orientada al diseño móvil, fiel a la identidad corporativa oficial de Global Salcai Utinsa (`#00778b` Teal, `#f2a900` Oro Canario, tarjetas limpias y tipografía institucional), estructurada en 7 pestañas:
1. **🗺️ Mapa en Vivo & Flota GPS**: Trazado vial de los corredores GC-1, GC-2 y GC-110 a Tafira, red de paradas y telemetría de guaguas en circulación con velocidad y ocupación en directo.
2. **🚏 Siguiente Parada**: Buscador por código oficial de 4 dígitos de la marquesina con llegadas en tiempo real y afluencia Poisson.
3. **🧭 ¿A dónde quieres ir?**: Calculadora predictiva de trayectos con hora de salida recomendada bajo Garantía de Llegada Bayesiana al 95% para exámenes en el Campus de Tafira, vuelos o citas médicas.
4. **💳 Fares & Cards (Saldo)**: Tarjeta virtual contactless (Wawa Joven, Bono Residente Canario, Bono Oro, TransGC) y monitor proactivo de cumplimiento de la regla de los 15 viajes mensuales para gratuidad total en Canarias.
5. **🏪 Vendedor de Tickets**: Red interactiva de oficinas centrales (San Telmo, Santa Catalina, Telde, Maspalomas, Aeropuerto LPA) y puntos oficiales de recarga con geolocalización.
6. **⚠️ Estado del Servicio**: Avisos de tráfico y red bayesiana causal con `pgmpy` simulando el impacto de retenciones en la GC-1 sobre retrasos y riesgo de pérdida de vuelos.
7. **🔬 Laboratorio de Datos (TFG ULPGC)**: Espacio académico interactivo con el panel de los 4 diagnósticos de Gauss-Markov, el Biplot PCA 2D con loadings, curvas de actualización bayesiana Beta-Binomial (HDI 95%), el DAG causal dirigido y el mapa de calor temporal de demoras.

---

# 4. Conclusiones y Trabajo Futuro

## 4.1. Conclusiones
* Se ha demostrado que la estandarización de horarios estáticos en el transporte de Gran Canaria genera asimetrías de información perjudiciales, especialmente tras la sobrecarga del sistema por la gratuidad.
* Los diagnósticos de Gauss-Markov demuestran la incapacidad matemática de los modelos lineales clásicos para capturar la variabilidad del tráfico congestionado, justificando de forma inapelable el uso de la Inferencia Bayesiana.
* La combinación de grafos causales con modelos predictivos de incertidumbre ofrece un marco de decisión infinitamente superior para el ciudadano y para la gestión insular de flota.

## 4.2. Trabajo Futuro y Transferencia Tecnológica
1. **Integración con SIRI / GTFS-RealTime**: Conexión directa en streaming con las API de billetaje y GPS de la Autoridad Única del Transporte de Gran Canaria (AUTGC).
2. **Ampliación Intermodal**: Integración de la red urbana de Guaguas Municipales de Las Palmas de Gran Canaria y la futura línea del Tren de Gran Canaria.
3. **Contenerización y Despliegue en la Nube**: Empaquetado Docker para su despliegue en la infraestructura tecnológica del Cabildo de Gran Canaria (SITCAN).

---

# 5. Referencias Bibliográficas

1. **Pearl, J.** (2009). *Causality: Models, Reasoning, and Inference*. Cambridge University Press, 2nd Edition.
2. **Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., & Rubin, D. B.** (2013). *Bayesian Data Analysis*. Chapman and Hall/CRC, 3rd Edition.
3. **Greene, W. H.** (2018). *Econometric Analysis*. Pearson, 8th Edition. (Capítulo de Supuestos de Gauss-Markov y Heterocedasticidad).
4. **Koller, D., & Friedman, N.** (2009). *Probabilistic Graphical Models: Principles and Techniques*. MIT Press.
5. **Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R.** (2000). *CRISP-DM 1.0: Step-by-step data mining guide*.
6. **Autoridad Única del Transporte de Gran Canaria (AUTGC)**. *Plan de Movilidad Sostenible de Gran Canaria (PMS)*. Cabildo de Gran Canaria.
7. **Naciones Unidas** (2015). *Transformar nuestro mundo: la Agenda 2030 para el Desarrollo Sostenible*. ODS 9, 11 y 13.
