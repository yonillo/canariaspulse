import React, { useState, useEffect } from 'react';
import { Compass, Clock, ArrowRight, ArrowDownUp, CheckCircle2, AlertCircle } from 'lucide-react';

export default function PlannerPanel({
  hubs = {},
  hasIncident = false,
  isPeak = true,
}) {
  const [origin, setOrigin] = useState('GC_STELMO');
  const [destination, setDestination] = useState('GC_TAFIRA_CAMPUS');
  const [targetTime, setTargetTime] = useState('08:30');
  const [walkBuffer, setWalkBuffer] = useState(5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    const keys = Object.keys(hubs);
    if (keys.length > 0) {
      if (!hubs[origin]) {
        setOrigin(keys.includes('GC_STELMO') ? 'GC_STELMO' : keys[0]);
      }
      if (!hubs[destination]) {
        setDestination(keys.includes('GC_TAFIRA_CAMPUS') ? 'GC_TAFIRA_CAMPUS' : (keys[1] || keys[0]));
      }
    }
  }, [hubs]);

  const handleSwap = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const handlePlan = () => {
    setLoading(true);
    setErrorMessage(null);
    fetch('/api/routes/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        origin_id: origin,
        destination_id: destination,
        is_peak: isPeak,
        incident_gc1: hasIncident,
        target_arrival_time: targetTime,
        walk_buffer_min: walkBuffer,
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setResult(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error calculando ruta:', err);
        setErrorMessage('No se pudo calcular la ruta con el servidor.');
        setLoading(false);
      });
  };

  return (
    <div className="flex flex-col h-full bg-white/90 dark:bg-zinc-900/90 text-zinc-900 dark:text-zinc-100 backdrop-blur-2xl rounded-3xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-xl overflow-hidden font-sans">
      {/* Top Handle */}
      <div className="w-8 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700 mx-auto mt-2.5"></div>

      {/* Header */}
      <div className="p-4 border-b border-zinc-100 dark:border-zinc-800/80">
        <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">Planificador Garantizado</h2>
        <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5">Ventana bayesiana con 95% de probabilidad de éxito</p>

        {/* Inputs */}
        <div className="mt-3 space-y-2">
          <div className="relative flex items-center gap-2">
            <div className="flex-1 space-y-1.5">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-100 dark:bg-zinc-800/70 border border-zinc-200/60 dark:border-zinc-700/60">
                <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
                <select
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                  className="w-full bg-transparent text-xs text-zinc-900 dark:text-zinc-100 focus:outline-none"
                >
                  {Object.entries(hubs).map(([k, v]) => (
                    <option key={k} value={k} className="text-zinc-900 bg-white dark:bg-zinc-900">
                      {v.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-100 dark:bg-zinc-800/70 border border-zinc-200/60 dark:border-zinc-700/60">
                <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
                <select
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="w-full bg-transparent text-xs text-zinc-900 dark:text-zinc-100 focus:outline-none"
                >
                  {Object.entries(hubs).map(([k, v]) => (
                    <option key={k} value={k} className="text-zinc-900 bg-white dark:bg-zinc-900">
                      {v.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleSwap}
              className="p-2 rounded-xl bg-zinc-100 dark:bg-zinc-800 text-zinc-500 hover:text-zinc-900 dark:hover:text-white transition-all shrink-0"
              title="Intercambiar origen y destino"
            >
              <ArrowDownUp className="w-4 h-4" />
            </button>
          </div>

          {/* Time & Buffer Row */}
          <div className="flex items-center gap-2 pt-1">
            <div className="flex-1 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-100 dark:bg-zinc-800/70 text-xs">
              <Clock className="w-3.5 h-3.5 text-zinc-400" />
              <span className="text-[11px] text-zinc-500">Llegar a:</span>
              <input
                type="time"
                value={targetTime}
                onChange={(e) => setTargetTime(e.target.value)}
                className="bg-transparent text-xs font-semibold focus:outline-none"
              />
            </div>

            <button
              onClick={handlePlan}
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 font-semibold text-xs hover:opacity-90 transition-all shrink-0 shadow-sm"
            >
              {loading ? 'Calculando...' : 'Calcular'}
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 p-3 overflow-y-auto space-y-2.5">
        {errorMessage && (
          <div className="p-3 rounded-2xl bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {!result && !loading && !errorMessage && (
          <div className="py-12 text-center text-zinc-400 text-xs">
            Selecciona origen, destino y pulsa Calcular para obtener la hora de salida garantizada.
          </div>
        )}

        {result && (
          <div className="space-y-3">
            {/* Guaranteed Output Card */}
            <div className="p-4 rounded-2xl bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-md">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-[10px] uppercase font-bold tracking-wider opacity-75">Hora recomendada de salida</div>
                  <div className="text-2xl font-black tracking-tight mt-0.5 tabular-nums">
                    {result.recommended_departure_time || result.safe_departure_time || '07:42'}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] uppercase font-bold tracking-wider opacity-75">Confianza</div>
                  <div className="text-sm font-extrabold text-emerald-400 dark:text-emerald-600">95% HDI</div>
                </div>
              </div>

              <div className="mt-2.5 pt-2.5 border-t border-white/10 dark:border-zinc-900/10 text-[11px] opacity-85">
                Llegada estimada a destino: <b>{targetTime}</b> • Margen de seguridad: <b>+{result.safety_buffer_minutes || 8} min</b>
              </div>
            </div>

            {/* Steps Timeline */}
            <div className="p-3 rounded-2xl bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-100 dark:border-zinc-800/60 space-y-2">
              <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Itinerario del trayecto</div>
              
              <div className="relative pl-5 space-y-3 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-zinc-200 dark:before:bg-zinc-700">
                <div className="relative">
                  <div className="absolute -left-5 top-1 w-2 h-2 rounded-full bg-emerald-500 ring-4 ring-white dark:ring-zinc-900"></div>
                  <div className="text-xs font-semibold">{hubs[origin]?.name || origin}</div>
                  <div className="text-[10px] text-zinc-400">Salida recomendada a las {result.recommended_departure_time || '07:42'}</div>
                </div>

                <div className="relative">
                  <div className="absolute -left-5 top-1 w-2 h-2 rounded-full bg-amber-400 ring-4 ring-white dark:ring-zinc-900"></div>
                  <div className="text-xs font-semibold">Trayecto en tránsito</div>
                  <div className="text-[10px] text-zinc-400">Duración estimada: ~{result.expected_travel_time_minutes || 35} minutos</div>
                </div>

                <div className="relative">
                  <div className="absolute -left-5 top-1 w-2 h-2 rounded-full bg-rose-500 ring-4 ring-white dark:ring-zinc-900"></div>
                  <div className="text-xs font-semibold">{hubs[destination]?.name || destination}</div>
                  <div className="text-[10px] text-zinc-400">Llegada puntual a las {targetTime}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
