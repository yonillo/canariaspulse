import React, { useState, useEffect } from 'react';
import { AlertOctagon, Zap, ShieldAlert, CloudRain, Clock, Plane, ArrowRight } from 'lucide-react';

export default function CausalRadarPanel({
  hasIncident = false,
  onToggleIncident = () => {},
  isPeak = true,
  onTogglePeak = () => {},
}) {
  const [rainMedianias, setRainMedianias] = useState(false);
  const [causalData, setCausalData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCausalInference = () => {
    setLoading(true);
    fetch('/api/causal/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incident_gc1: hasIncident,
        is_peak: isPeak,
        rain_medianias: rainMedianias,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setCausalData(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchCausalInference();
  }, [hasIncident, isPeak, rainMedianias]);

  const flightRisk = causalData?.summary?.p_flight_risk
    ? Math.round(causalData.summary.p_flight_risk * 100)
    : hasIncident
    ? 48
    : 6;

  const l30Delay = causalData?.summary?.p_l30_delay
    ? Math.round(causalData.summary.p_l30_delay * 100)
    : hasIncident
    ? 72
    : 30;

  const gc1Congestion = causalData?.summary?.p_gc1_congestion
    ? Math.round(causalData.summary.p_gc1_congestion * 100)
    : hasIncident
    ? 86
    : 18;

  const tafiraDelay = causalData?.summary?.p_tafira_delay
    ? Math.round(causalData.summary.p_tafira_delay * 100)
    : rainMedianias
    ? 68
    : 22;

  return (
    <div className="flex flex-col h-full bg-slate-900/95 text-slate-100 backdrop-blur-2xl rounded-3xl border border-slate-700/80 shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-500 to-rose-700 flex items-center justify-center text-white shadow-md">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-extrabold text-white">Radar de Resiliencia Insular & Causalidad Bayesiana</h2>
            <p className="text-[11px] text-amber-400 font-semibold">Simulador de Desconexión y Efecto Dominó en Autovías y Ferries</p>
          </div>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {/* Controles de Escenarios */}
        <div className="p-3.5 rounded-2xl bg-slate-800/70 border border-slate-700/60 space-y-2.5">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Simulador de Perturbaciones (Intervenciones do-calculus en Grafo DAG)
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <button
              onClick={onToggleIncident}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                hasIncident
                  ? 'bg-red-500/20 border-red-500/80 text-white'
                  : 'bg-slate-900/70 border-slate-700 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold">Colapso GC-1 / TF-5</span>
                <span className={`w-2 h-2 rounded-full ${hasIncident ? 'bg-red-500 animate-ping' : 'bg-slate-600'}`}></span>
              </div>
              <div className="text-[9px] text-slate-400 mt-1">Jinámar / Nudo Anchieta</div>
            </button>

            <button
              onClick={onTogglePeak}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                isPeak
                  ? 'bg-amber-500/20 border-amber-500/80 text-white'
                  : 'bg-slate-900/70 border-slate-700 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold">Hora Punta Insular</span>
                <Clock className="w-3.5 h-3.5 text-amber-400" />
              </div>
              <div className="text-[9px] text-slate-400 mt-1">07:15 - 09:15 h</div>
            </button>

            <button
              onClick={() => setRainMedianias(!rainMedianias)}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                rainMedianias
                  ? 'bg-cyan-500/20 border-cyan-500/80 text-white'
                  : 'bg-slate-900/70 border-slate-700 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold">Temporal / Niebla</span>
                <CloudRain className="w-3.5 h-3.5 text-cyan-400" />
              </div>
              <div className="text-[9px] text-slate-400 mt-1">Medianías / Mar de fondo</div>
            </button>
          </div>
        </div>

        {/* Medidores de Probabilidad Causal */}
        <div className="space-y-3">
          {/* Riesgo Pérdida de Vuelo en Gando */}
          <div className="p-3.5 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/80 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center">
                  <Plane className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-white">Riesgo Pérdida Vuelo (Aeropuerto LPA)</div>
                  <div className="text-[10px] text-slate-400">Inferencia condicional exacta en pgmpy</div>
                </div>
              </div>
              <span className={`text-base font-black ${flightRisk > 30 ? 'text-red-400' : 'text-emerald-400'}`}>
                {flightRisk}%
              </span>
            </div>

            <div className="w-full h-2.5 rounded-full bg-slate-950 overflow-hidden">
              <div
                style={{ width: `${flightRisk}%` }}
                className={`h-full transition-all duration-500 ${
                  flightRisk > 30 ? 'bg-gradient-to-r from-amber-500 to-red-500' : 'bg-emerald-500'
                }`}
              ></div>
            </div>

            {hasIncident && (
              <div className="text-[10px] text-red-300/90 bg-red-500/10 p-2 rounded-xl flex items-center gap-1.5 border border-red-500/20">
                <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />
                <span><b>Alerta crítica:</b> Un accidente en la GC-1 multiplica por <b>x8</b> la probabilidad de perder un vuelo.</span>
              </div>
            )}
          </div>

          {/* Retraso Línea 30 (Sur) */}
          <div className="p-3.5 rounded-2xl bg-slate-800/70 border border-slate-700/70 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">P(Retraso Severo Línea 30 Sur)</span>
              <span className="font-black text-amber-400">{l30Delay}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
              <div
                style={{ width: `${l30Delay}%` }}
                className="h-full bg-gradient-to-r from-amber-400 to-amber-500 transition-all duration-500"
              ></div>
            </div>
          </div>

          {/* Retraso Línea 303 (Tafira) */}
          <div className="p-3.5 rounded-2xl bg-slate-800/70 border border-slate-700/70 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">P(Retraso Línea 303 Tafira / Campus)</span>
              <span className="font-black text-cyan-400">{tafiraDelay}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
              <div
                style={{ width: `${tafiraDelay}%` }}
                className="h-full bg-cyan-400 transition-all duration-500"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
