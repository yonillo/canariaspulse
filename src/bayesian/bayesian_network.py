"""Módulo de Redes Bayesianas e Inferencia Causal para la Red Insular de Gran Canaria (Bloque 2 Tema 6).

Implementa:
- Grafo Causal Acíclico Dirigido (DAG) que modela las interdependencias del tráfico insular.
- Nodos causales: Clima en Medianías, Incidentes en GC-1, Congestión en San Telmo,
  Atasco en Hoya de la Plata, Retrasos en Líneas del Sur (L30/L50), Retraso hacia Tafira/San Mateo (L303)
  y Riesgo de Pérdida de Conexión en el Aeropuerto de Gran Canaria.
- Inferencia exacta mediante el algoritmo de Eliminación de Variables (Variable Elimination).
- Razonamiento predictivo (causa -> efecto) y diagnóstico abductivo (efecto observado -> causa probable).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
try:
    from pgmpy.models import DiscreteBayesianNetwork as BayesianNetModel
except ImportError:
    from pgmpy.models import BayesianNetwork as BayesianNetModel


class GranCanariaBayesianNetwork:
    """Red Bayesiana del sistema de transporte interurbano y autopistas de Gran Canaria."""

    def __init__(self):
        # 1. Definición de la estructura de aristas dirigidas (DAG)
        self.model = BayesianNetModel([
            ("Clima_Medianias", "Retraso_L303_Medianias"),
            ("Incidente_GC1", "Atasco_HoyaPlata"),
            ("Congestion_SanTelmo", "Atasco_HoyaPlata"),
            ("Congestion_SanTelmo", "Retraso_L303_Medianias"),
            ("Atasco_HoyaPlata", "Retraso_L30_Sur"),
            ("Retraso_L30_Sur", "Riesgo_Vuelo_Aeropuerto"),
        ])

        # 2. Definición de las Tablas de Probabilidad Condicional (CPDs)
        # Nodos raíz:
        # Clima_Medianias: 0 = Despejado (88%), 1 = Lluvia/Niebla (12%)
        cpd_clima = TabularCPD(
            variable="Clima_Medianias",
            variable_card=2,
            values=[[0.88], [0.12]],
            state_names={"Clima_Medianias": ["Despejado", "Lluvia_Niebla"]}
        )

        # Incidente_GC1: 0 = No (90%), 1 = Sí (10%)
        cpd_incidente = TabularCPD(
            variable="Incidente_GC1",
            variable_card=2,
            values=[[0.90], [0.10]],
            state_names={"Incidente_GC1": ["No", "Si"]}
        )

        # Congestion_SanTelmo: 0 = Baja (70%), 1 = Alta (30%)
        cpd_santelmo = TabularCPD(
            variable="Congestion_SanTelmo",
            variable_card=2,
            values=[[0.70], [0.30]],
            state_names={"Congestion_SanTelmo": ["Baja", "Alta"]}
        )

        # Nodo Atasco_HoyaPlata (Salida GC-1) | Incidente_GC1, Congestion_SanTelmo
        # Columnas: (No, Baja), (No, Alta), (Si, Baja), (Si, Alta)
        # Estados: 0 = Fluido, 1 = Colapso
        cpd_hoya_plata = TabularCPD(
            variable="Atasco_HoyaPlata",
            variable_card=2,
            values=[
                [0.85, 0.45, 0.15, 0.05],  # Fluido
                [0.15, 0.55, 0.85, 0.95],  # Colapso
            ],
            evidence=["Incidente_GC1", "Congestion_SanTelmo"],
            evidence_card=[2, 2],
            state_names={
                "Atasco_HoyaPlata": ["Fluido", "Colapso"],
                "Incidente_GC1": ["No", "Si"],
                "Congestion_SanTelmo": ["Baja", "Alta"],
            }
        )

        # Nodo Retraso_L30_Sur | Atasco_HoyaPlata
        # Estados: 0 = Puntual, 1 = Retraso
        cpd_l30 = TabularCPD(
            variable="Retraso_L30_Sur",
            variable_card=2,
            values=[
                [0.88, 0.20],  # Puntual
                [0.12, 0.80],  # Retraso
            ],
            evidence=["Atasco_HoyaPlata"],
            evidence_card=[2],
            state_names={
                "Retraso_L30_Sur": ["Puntual", "Retraso"],
                "Atasco_HoyaPlata": ["Fluido", "Colapso"],
            }
        )

        # Nodo Retraso_L303_Medianias | Clima_Medianias, Congestion_SanTelmo
        # Columnas: (Despejado, Baja), (Despejado, Alta), (Lluvia, Baja), (Lluvia, Alta)
        cpd_l303 = TabularCPD(
            variable="Retraso_L303_Medianias",
            variable_card=2,
            values=[
                [0.86, 0.50, 0.40, 0.15],  # Puntual
                [0.14, 0.50, 0.60, 0.85],  # Retraso
            ],
            evidence=["Clima_Medianias", "Congestion_SanTelmo"],
            evidence_card=[2, 2],
            state_names={
                "Retraso_L303_Medianias": ["Puntual", "Retraso"],
                "Clima_Medianias": ["Despejado", "Lluvia_Niebla"],
                "Congestion_SanTelmo": ["Baja", "Alta"],
            }
        )

        # Nodo Riesgo_Vuelo_Aeropuerto | Retraso_L30_Sur
        # Estados: 0 = Bajo_Riesgo, 1 = Alto_Riesgo
        cpd_aeropuerto = TabularCPD(
            variable="Riesgo_Vuelo_Aeropuerto",
            variable_card=2,
            values=[
                [0.94, 0.35],  # Bajo
                [0.06, 0.65],  # Alto
            ],
            evidence=["Retraso_L30_Sur"],
            evidence_card=[2],
            state_names={
                "Riesgo_Vuelo_Aeropuerto": ["Bajo", "Alto"],
                "Retraso_L30_Sur": ["Puntual", "Retraso"],
            }
        )

        self.model.add_cpds(
            cpd_clima,
            cpd_incidente,
            cpd_santelmo,
            cpd_hoya_plata,
            cpd_l30,
            cpd_l303,
            cpd_aeropuerto
        )
        self.model.check_model()
        self.infer_engine = VariableElimination(self.model)

    def query_probability(
        self,
        variables: List[str],
        evidence: Optional[Dict[str, str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """Realiza inferencia probabilística exacta por eliminación de variables dada una evidencia observada."""
        evidence = evidence or {}
        query_res = self.infer_engine.query(variables=variables, evidence=evidence, show_progress=False)

        results = {}
        # Si se consulta una sola variable o varias
        if hasattr(query_res, "variables") and len(query_res.variables) == 1:
            var_name = query_res.variables[0]
            state_names = self.model.get_cpds(var_name).state_names[var_name]
            probs = {state_names[i]: round(float(query_res.values[i]), 4) for i in range(len(state_names))}
            results[var_name] = probs
        else:
            for v in variables:
                sub_res = self.infer_engine.query(variables=[v], evidence=evidence, show_progress=False)
                state_names = self.model.get_cpds(v).state_names[v]
                probs = {state_names[i]: round(float(sub_res.values[i]), 4) for i in range(len(state_names))}
                results[v] = probs

        return results

    def get_structure_graph(self) -> List[Dict[str, str]]:
        """Retorna las aristas de la red causal para su renderizado interactivo en la UI."""
        return [{"source": u, "target": v} for u, v in self.model.edges()]
