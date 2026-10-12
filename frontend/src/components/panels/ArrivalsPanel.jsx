import React, { useState, useEffect } from 'react';
import { Bus, RefreshCw, MapPin, CheckCircle2, ChevronRight } from 'lucide-react';

export default function ArrivalsPanel({
  selectedStop,
  onSelectStop = () => {},
  hubs = {},
  hasIncident = false,
  isPeak = true,
}) {
  const [departures, setDepartures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('');

  const activeStopId = selectedStop?.hub_id || selectedStop?.id || selectedStop?.code || 'GC_STELMO';
  const activeStopName = selectedStop?.name || 'Estación de Guaguas San Telmo';
  const activeStopLocality = selectedStop?.locality || selectedStop?.island || 'Gran Canaria';

  const fetchDepartures = () => {
    setLoading(true);
    fetch(`/api/stops/${encodeURIComponent(activeStopId)}/departures?incident_gc1=${hasIncident}&is_peak=${isPeak}`)
      .then((res) => res.json())
      .then((data) => {
        setDepartures(data.departures || []);
        setLastUpdated(data.timestamp || new Date().toLocaleTimeString().slice(0, 5));
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDepartures();
    const interval = setInterval(fetchDepartures, 12000);
    return () => clearInterval(interval);
  }, [activeStopId, hasIncident, isPeak]);

  return (
    <div className="flex flex-col h-full bg-white/90 dark:bg-zinc-900/90 text-zinc-900 dark:text-zinc-100 backdrop-blur-2xl rounded-3xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-xl overflow-hidden font-sans">
      {/* Top Handle */}
      <div className="w-8 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700 mx-auto mt-2.5"></div>

      {/* Header */}
      <div className="p-4 border-b border-zinc-100 dark:border-zinc-800/80">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-zinc-500 dark:text-zinc-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>{activeStopLocality}</span>
              <span>•</span>
              <span className="text-zinc-400">GTFS Oficial</span>
            </div>
            <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100 mt-0.5 tracking-tight truncate">
              {activeStopName}
            </h2>
          </div>

          <button
            onClick={fetchDepartures}
            className="p-1.5 rounded-xl text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors shrink-0"
            title="Actualizar salidas"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Quick Hub Filter */}
        <div className="flex items-center gap-1.5 mt-3 overflow-x-auto pb-1 scrollbar-none">
          {Object.entries(hubs).slice(0, 10).map(([hubKey, hubData]) => {
            const isSelected = activeStopId === hubKey || activeStopId === hubData.stop_id;
            const shortName = hubData.name
              .replace('Estación de Guaguas de ', '')
              .replace('Intercambiador ', '')
              .replace('Puerto de ', 'Pto. ')
              .split(' (')[0];

            return (
              <button
                key={hubKey}
                onClick={() => onSelectStop({ ...hubData, hub_id: hubKey, id: hubKey })}
                className={`px-2.5 py-1 rounded-full text-[11px] font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-sm'
                    : 'bg-zinc-100 dark:bg-zinc-800/70 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
                }`}
              >
                {shortName}
              </button>
            );
          })}
        </div>
      </div>

      {/* Salidas en tiempo real */}
      <div className="flex-1 p-3 overflow-y-auto space-y-2">
        <div className="flex items-center justify-between text-[11px] font-medium text-zinc-400 px-1">
          <span>SALIDAS ESTIMADAS</span>
          <span>{lastUpdated && `Act: ${lastUpdated}`}</span>
        </div>

        {departures.length === 0 ? (
          <div className="py-12 text-center text-zinc-400 text-xs">
            {loading ? 'Consultando horarios oficiales GTFS...' : 'No hay salidas inmediatas para esta parada.'}
          </div>
        ) : (
          departures.map((dep, idx) => {
            const isUrgent = dep.arrival_window.includes('1 -') || dep.arrival_window.includes('2 -') || dep.arrival_window.includes('3 -');
            const isCrowded = dep.crowding?.includes('Saturada') || dep.crowding?.includes('Alta');
            const isMedium = dep.crowding?.includes('media') || dep.crowding?.includes('Bastante');

            return (
              <div
                key={idx}
                className="p-3 rounded-2xl bg-zinc-50 dark:bg-zinc-800/50 hover:bg-zinc-100 dark:hover:bg-zinc-800/80 transition-all border border-zinc-100 dark:border-zinc-800/60 flex items-center justify-between gap-3"
              >
                {/* Line & Destination */}
                <div className="flex items-center gap-3 min-w-0">
                  <span
                    className="w-10 h-7 rounded-lg text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm"
                    style={{ backgroundColor: dep.color || '#3b82f6' }}
                  >
                    {dep.line}
                  </span>
                  <div className="min-w-0">
                    <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 truncate">
                      {dep.destination}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-zinc-500 dark:text-zinc-400">
                      <span>{dep.agency || 'Canarias'}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            isCrowded ? 'bg-rose-500' : isMedium ? 'bg-amber-400' : 'bg-emerald-500'
                          }`}
                        ></span>
                        <span>{isCrowded ? 'Alta ocupación' : isMedium ? 'Aforo medio' : 'Asientos libres'}</span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* Timing */}
                <div className="text-right shrink-0">
                  <div className={`text-xs font-bold tabular-nums ${isUrgent ? 'text-amber-500' : 'text-zinc-900 dark:text-zinc-100'}`}>
                    {dep.arrival_window}
                  </div>
                  <div className="text-[10px] text-zinc-400 tabular-nums">
                    {dep.expected_time}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
