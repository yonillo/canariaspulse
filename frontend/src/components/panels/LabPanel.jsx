import React, { useState } from 'react';
import { FlaskConical, Play, CheckCircle2, TrendingUp, AlertTriangle, Cpu, Layers } from 'lucide-react';

export default function LabPanel() {
  const [activeSection, setActiveSection] = useState('optimization'); // optimization, gauss, distributions
  const [optProblem, setOptProblem] = useState('milp');
  const [busBudget, setBusBudget] = useState(25);
  const [optResult, setOptResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRunOptimization = () => {
    setLoading(true);
    fetch('/api/optimization/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        problem: optProblem,
        bus_budget: busBudget,
        driver_hours: 60.0,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setOptResult(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/95 text-slate-100 backdrop-blur-2xl rounded-3xl border border-slate-700/80 shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-md">
              <FlaskConical className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-extrabold text-white">Laboratorio TFG (ULPGC)</h2>
              <p className="text-[11px] text-indigo-400 font-semibold">Ciencia e Ingeniería de Datos • Escuela de Informática</p>
            </div>
          </div>
        </div>

        {/* Subtabs */}
        <div className="flex items-center gap-1 mt-3 p-1 rounded-xl bg-slate-800/80 border border-slate-700">
          <button
            onClick={() => setActiveSection('optimization')}
            className={`flex-1 py-1 rounded-lg text-[11px] font-bold transition-all ${
              activeSection === 'optimization' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Optimización (Temas 1-4)
          </button>
          <button
            onClick={() => setActiveSection('gauss')}
            className={`flex-1 py-1 rounded-lg text-[11px] font-bold transition-all ${
              activeSection === 'gauss' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Gauss-Markov (MCO)
          </button>
          <button
            onClick={() => setActiveSection('distributions')}
            className={`flex-1 py-1 rounded-lg text-[11px] font-bold transition-all ${
              activeSection === 'distributions' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Bondad Ajuste MLE
          </button>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {/* SECCIÓN 1: OPTIMIZACIÓN MATEMÁTICA */}
        {activeSection === 'optimization' && (
          <div className="space-y-3">
            <div className="p-3 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                Seleccionar Problema de Optimización Operativa
              </label>

              <div className="grid grid-cols-2 gap-1.5">
                <button
                  onClick={() => { setOptProblem('milp'); setOptResult(null); }}
                  className={`p-2 rounded-xl text-left border text-xs font-bold transition-all ${
                    optProblem === 'milp'
                      ? 'bg-indigo-600/30 border-indigo-400 text-white'
                      : 'bg-slate-900 border-slate-700 text-slate-400'
                  }`}
                >
                  <div className="text-white">MILP Despacho Flota</div>
                  <div className="text-[9px] font-normal text-slate-400">Temas 1 y 3 (HiGHS / Simplex)</div>
                </button>

                <button
                  onClick={() => { setOptProblem('newton'); setOptResult(null); }}
                  className={`p-2 rounded-xl text-left border text-xs font-bold transition-all ${
                    optProblem === 'newton'
                      ? 'bg-indigo-600/30 border-indigo-400 text-white'
                      : 'bg-slate-900 border-slate-700 text-slate-400'
                  }`}
                >
                  <div className="text-white">Newton vs Gradiente</div>
                  <div className="text-[9px] font-normal text-slate-400">Tema 2 (Hessiano exacto)</div>
                </button>

                <button
                  onClick={() => { setOptProblem('lagrange'); setOptResult(null); }}
                  className={`p-2 rounded-xl text-left border text-xs font-bold transition-all ${
                    optProblem === 'lagrange'
                      ? 'bg-indigo-600/30 border-indigo-400 text-white'
                      : 'bg-slate-900 border-slate-700 text-slate-400'
                  }`}
                >
                  <div className="text-white">Lagrange Frecuencias</div>
                  <div className="text-[9px] font-normal text-slate-400">Tema 3.2 (Condiciones KKT)</div>
                </button>

                <button
                  onClick={() => { setOptProblem('tsp_sa'); setOptResult(null); }}
                  className={`p-2 rounded-xl text-left border text-xs font-bold transition-all ${
                    optProblem === 'tsp_sa'
                      ? 'bg-indigo-600/30 border-indigo-400 text-white'
                      : 'bg-slate-900 border-slate-700 text-slate-400'
                  }`}
                >
                  <div className="text-white">TSP Insular (SA / GA)</div>
                  <div className="text-[9px] font-normal text-slate-400">Tema 4 (Metaheurísticas)</div>
                </button>
              </div>

              {optProblem === 'milp' && (
                <div className="pt-2">
                  <div className="flex justify-between text-xs font-bold text-slate-300 mb-1">
                    <span>Límite Flota Disponible:</span>
                    <span className="text-amber-400">{busBudget} guaguas</span>
                  </div>
                  <input
                    type="range"
                    min="15"
                    max="45"
                    value={busBudget}
                    onChange={(e) => setBusBudget(Number(e.target.value))}
                    className="w-full accent-amber-400"
                  />
                </div>
              )}

              <button
                onClick={handleRunOptimization}
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-extrabold text-xs uppercase tracking-wider shadow-lg shadow-indigo-500/25 hover:opacity-95 transition-all flex items-center justify-center gap-1.5 mt-2"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>{loading ? 'Resolviendo con Solver...' : 'Ejecutar Algoritmo de Optimización'}</span>
              </button>
            </div>

            {/* Resultado de la Optimización */}
            {optResult && (
              <div className="p-3.5 rounded-2xl bg-indigo-950/40 border border-indigo-500/40 space-y-2 text-xs">
                <div className="flex items-center justify-between font-extrabold text-white">
                  <span>{optResult.problem}</span>
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Convergido
                  </span>
                </div>

                {optProblem === 'milp' && (
                  <div className="space-y-1.5 text-slate-300">
                    <div className="flex justify-between">
                      <span>Guaguas Asignadas:</span>
                      <b className="text-white">{optResult.total_buses} unidades</b>
                    </div>
                    <div className="flex justify-between">
                      <span>Demanda Atendida:</span>
                      <b className="text-emerald-400">{Math.round(optResult.coverage_ratio * 100)}%</b>
                    </div>
                    <div className="flex justify-between">
                      <span>Coste Total Operativo:</span>
                      <b className="text-amber-400">{optResult.total_cost_eur?.toFixed(2)} €</b>
                    </div>
                    <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-700">
                      Solver: <b>{optResult.solver}</b> (Precios sombra duales calculados).
                    </div>
                  </div>
                )}

                {optProblem === 'newton' && (
                  <div className="space-y-1.5 text-slate-300">
                    <div className="flex justify-between">
                      <span>Iteraciones Método de Newton:</span>
                      <b className="text-emerald-400">{optResult.newton_method?.iterations} iteraciones</b>
                    </div>
                    <div className="flex justify-between">
                      <span>Iteraciones Descenso por Gradiente:</span>
                      <b className="text-amber-400">{optResult.gradient_descent?.iterations} iteraciones</b>
                    </div>
                    <div className="p-2 rounded-xl bg-slate-900 text-amber-300 font-bold text-[11px]">
                      🚀 El Método de Newton converge <b>{optResult.speedup_factor}x</b> más rápido gracias a la matriz Hessiana exacta.
                    </div>
                  </div>
                )}

                {optProblem === 'tsp_sa' && (
                  <div className="space-y-1.5 text-slate-300">
                    <div className="flex justify-between">
                      <span>Distancia Recocido Simulado:</span>
                      <b className="text-emerald-400">{optResult.simulated_annealing?.best_distance_km} km</b>
                    </div>
                    <div className="flex justify-between">
                      <span>Distancia Algoritmo Genético:</span>
                      <b className="text-cyan-400">{optResult.genetic_algorithm?.best_distance_km} km</b>
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Ruta óptima de 10 hubs estratégicos completada en circuito cerrado insular.
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* SECCIÓN 2: GAUSS-MARKOV */}
        {activeSection === 'gauss' && (
          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-2xl bg-slate-800/80 border border-slate-700 space-y-2">
              <div className="font-bold text-white text-sm">Ruptura del Teorema de Gauss-Markov</div>
              <p className="text-slate-300 text-[11px] leading-relaxed">
                El modelo MCO clásico ($R^2 = 0,7703$) quiebra en tráfico insular debido a la presencia masiva de heterocedasticidad.
              </p>

              <div className="grid grid-cols-2 gap-2 mt-2">
                <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/30">
                  <div className="text-[10px] text-red-300 font-bold">Breusch-Pagan</div>
                  <div className="text-base font-black text-red-400 mt-0.5">p &lt; 0.0001</div>
                  <div className="text-[9px] text-slate-400">Heterocedasticidad Severa</div>
                </div>

                <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/30">
                  <div className="text-[10px] text-red-300 font-bold">Jarque-Bera</div>
                  <div className="text-base font-black text-red-400 mt-0.5">p &lt; 0.0001</div>
                  <div className="text-[9px] text-slate-400">Residuos Asimétricos</div>
                </div>

                <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30">
                  <div className="text-[10px] text-amber-300 font-bold">Durbin-Watson</div>
                  <div className="text-base font-black text-amber-400 mt-0.5">0.805</div>
                  <div className="text-[9px] text-slate-400">Autocorrelación Positiva</div>
                </div>

                <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                  <div className="text-[10px] text-emerald-300 font-bold">VIF Máximo</div>
                  <div className="text-base font-black text-emerald-400 mt-0.5">1.29 &lt; 5.0</div>
                  <div className="text-[9px] text-slate-400">Sin Multicolinealidad</div>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-900 text-amber-300 text-[10px] font-semibold">
                💡 Justificación matemática para el salto al paradigma Bayesiano y HDI 95%.
              </div>
            </div>
          </div>
        )}

        {/* SECCIÓN 3: BONDAD DE AJUSTE MLE */}
        {activeSection === 'distributions' && (
          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-2xl bg-slate-800/80 border border-slate-700 space-y-2">
              <div className="font-bold text-white text-sm">Selección de Modelo de Distribución (MLE)</div>
              <p className="text-slate-300 text-[11px]">
                Ajuste paramétrico de 14.889 expediciones continuas evaluadas con AIC y BIC:
              </p>

              <div className="space-y-2">
                <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-between">
                  <div>
                    <div className="font-black text-white text-sm">1. Log-Normal (Óptimo)</div>
                    <div className="text-[10px] text-slate-300">Log-Likelihood: -54.839,7</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-black text-emerald-400">AIC: 109.685,4</div>
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500 text-slate-950">
                      GANADOR
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-slate-200">2. Gamma</div>
                    <div className="text-[10px] text-slate-400">Log-Likelihood: -55.067,5</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-slate-300">AIC: 110.141,0</div>
                    <div className="text-[9px] text-slate-500">ΔAIC = +455,6</div>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-slate-200">3. Weibull</div>
                    <div className="text-[10px] text-slate-400">Log-Likelihood: -56.859,6</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-slate-300">AIC: 113.725,2</div>
                    <div className="text-[9px] text-slate-500">ΔAIC = +4.039,8</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
