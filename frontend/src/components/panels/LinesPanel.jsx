import React, { useState } from 'react';
import { Route, Search, ChevronRight, Bus, Ship } from 'lucide-react';

export default function LinesPanel({
  lines = [],
  selectedLine = null,
  onSelectLine = () => {},
}) {
  const [operatorFilter, setOperatorFilter] = useState('ALL');
  const [lineSearch, setLineSearch] = useState('');

  const filteredLines = lines.filter((line) => {
    // Filtro operador
    if (operatorFilter === 'GLOBAL') {
      if (line.operator !== 'GLOBAL' && line.agency_id !== 'GLOBAL') return false;
    } else if (operatorFilter === 'TITSA') {
      if (line.operator !== 'TITSA' && line.agency_id !== 'TITSA') return false;
    } else if (operatorFilter === 'GUAGUAS_MUNICIPALES') {
      if (line.operator !== 'GUAGUAS_MUNICIPALES' && line.agency_id !== 'GUAGUAS') return false;
    } else if (operatorFilter === 'MARITIME') {
      if (line.operator !== 'FRED_OLSEN' && line.operator !== 'NAVIERA_ARMAS' && line.operator !== 'BALEARIA' && line.agency_id !== 'MARITIMO') return false;
    }

    // Filtro búsqueda
    if (lineSearch.trim()) {
      const q = lineSearch.toLowerCase();
      const num = (line.line_id || line.short_name || line.line || '').toString().toLowerCase();
      const name = (line.name || line.long_name || '').toLowerCase();
      const dest = (line.destination || '').toLowerCase();
      return num.includes(q) || name.includes(q) || dest.includes(q);
    }
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-white/90 dark:bg-zinc-900/90 text-zinc-900 dark:text-zinc-100 backdrop-blur-2xl rounded-3xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-xl overflow-hidden font-sans">
      {/* Top Handle */}
      <div className="w-8 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700 mx-auto mt-2.5"></div>

      {/* Header */}
      <div className="p-4 border-b border-zinc-100 dark:border-zinc-800/80">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">Líneas y Rutas GTFS</h2>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5">241 líneas oficiales en el archipiélago</p>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
            {filteredLines.length}
          </span>
        </div>

        {/* Buscador de Líneas */}
        <div className="mt-3 relative">
          <input
            type="text"
            placeholder="Buscar por número o destino (01, 10, 12, Agaete...)"
            value={lineSearch}
            onChange={(e) => setLineSearch(e.target.value)}
            className="w-full px-3 py-1.5 rounded-xl bg-zinc-100 dark:bg-zinc-800/70 text-xs text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-400"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 mt-2.5 overflow-x-auto pb-1 scrollbar-none">
          {[
            { id: 'ALL', label: 'Todas' },
            { id: 'TITSA', label: 'TITSA (TF)' },
            { id: 'GUAGUAS_MUNICIPALES', label: 'Guaguas (GC)' },
            { id: 'GLOBAL', label: 'Global (GC)' },
            { id: 'MARITIME', label: 'Marítimo' },
          ].map((op) => (
            <button
              key={op.id}
              onClick={() => setOperatorFilter(op.id)}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium whitespace-nowrap transition-all ${
                operatorFilter === op.id
                  ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-sm'
                  : 'bg-zinc-100 dark:bg-zinc-800/70 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
              }`}
            >
              {op.label}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Líneas */}
      <div className="flex-1 p-3 overflow-y-auto space-y-1.5">
        {filteredLines.map((line) => {
          const lineId = line.line_id || line.short_name || line.line;
          const isSelected = selectedLine === lineId;
          const lineName = line.name || line.long_name || line.destination || '';
          const isMaritime = line.mode === 'maritime' || line.operator === 'FRED_OLSEN' || line.operator === 'BALEARIA' || line.operator === 'NAVIERA_ARMAS';

          return (
            <button
              key={lineId}
              onClick={() => onSelectLine(isSelected ? null : lineId)}
              className={`w-full p-2.5 rounded-2xl flex items-center justify-between text-left transition-all ${
                isSelected
                  ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-sm'
                  : 'bg-zinc-50 dark:bg-zinc-800/40 hover:bg-zinc-100 dark:hover:bg-zinc-800/70 text-zinc-900 dark:text-zinc-100 border border-zinc-100 dark:border-zinc-800/40'
              }`}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <span
                  className="w-10 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 text-white shadow-xs"
                  style={{ backgroundColor: line.color || '#3b82f6' }}
                >
                  {lineId}
                </span>
                <div className="min-w-0">
                  <div className="text-xs font-semibold truncate leading-snug">{lineName}</div>
                  <div className={`text-[10px] ${isSelected ? 'text-zinc-300 dark:text-zinc-600' : 'text-zinc-400'}`}>
                    {line.operator || (isMaritime ? 'Fast Ferry' : 'Interurbano')} {line.frequency ? `• c/${line.frequency}m` : ''}
                  </div>
                </div>
              </div>
              <ChevronRight className={`w-4 h-4 shrink-0 ${isSelected ? 'text-white dark:text-zinc-900' : 'text-zinc-300 dark:text-zinc-600'}`} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
