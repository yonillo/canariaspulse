import React, { useState, useEffect } from 'react';
import { Search, AlertTriangle, Bus, MapPin, X, Sparkles, CheckCircle2 } from 'lucide-react';

export default function TopNavigation({
  onSearchSelect = () => {},
  hasIncident = false,
  onToggleIncident = () => {},
  isPeak = true,
  onTogglePeak = () => {},
  vehiclesCount = 18,
  gtfsSummary = null,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [islandFilter, setIslandFilter] = useState('Todas');

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(() => {
      const url = `/api/stops/search?q=${encodeURIComponent(searchQuery)}${
        islandFilter !== 'Todas' ? `&island=${encodeURIComponent(islandFilter)}` : ''
      }`;
      fetch(url)
        .then((res) => res.json())
        .then((data) => {
          setSearchResults(data.results || []);
        })
        .catch(() => {});
    }, 200);

    return () => clearTimeout(timer);
  }, [searchQuery, islandFilter]);

  return (
    <div className="absolute top-4 left-4 right-4 z-[1000] flex flex-col md:flex-row items-center justify-between gap-2.5 pointer-events-none font-sans">
      {/* Search & Island selector capsule */}
      <div className="flex items-center gap-2 w-full md:w-auto pointer-events-auto">
        {/* Brand Chip */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-2xl bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-sm shrink-0">
          <div className="w-6 h-6 rounded-lg bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center text-white dark:text-zinc-950 font-black text-xs">
            C
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-bold text-xs tracking-tight text-zinc-900 dark:text-zinc-100">Canarias</span>
            <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">MaaS</span>
          </div>
        </div>

        {/* Minimalist Search Box */}
        <div className="relative flex-1 md:w-96">
          <div className="flex items-center gap-2 px-3 py-2 rounded-2xl bg-white/90 dark:bg-zinc-900/90 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200/80 dark:border-zinc-800/80 backdrop-blur-xl transition-all focus-within:ring-2 focus-within:ring-zinc-400 dark:focus-within:ring-zinc-600">
            <Search className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
            <input
              type="text"
              placeholder="Buscar entre 4.771 paradas GTFS (Tenerife, Gran Canaria, puertos)..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsSearching(true);
              }}
              onFocus={() => setIsSearching(true)}
              className="w-full bg-transparent text-xs text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 focus:outline-none"
            />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSearchResults([]);
                  setIsSearching(false);
                }}
                className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Autocomplete Results */}
          {isSearching && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1.5 py-1 bg-white/95 dark:bg-zinc-900/95 backdrop-blur-2xl rounded-2xl shadow-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden max-h-72 overflow-y-auto z-50">
              {searchResults.map((stop) => (
                <button
                  key={`${stop.source || 'stop'}-${stop.id || stop.code}`}
                  onClick={() => {
                    onSearchSelect(stop);
                    setSearchQuery(stop.name);
                    setIsSearching(false);
                  }}
                  className="w-full px-3.5 py-2 text-left hover:bg-zinc-100 dark:hover:bg-zinc-800/60 flex items-center justify-between transition-colors border-b border-zinc-100 dark:border-zinc-800/40 last:border-0"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
                    <div className="truncate">
                      <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 truncate">{stop.name}</div>
                      <div className="text-[10px] text-zinc-500 dark:text-zinc-400">
                        {stop.locality || 'Canarias'} {stop.agency_id ? `• ${stop.agency_id}` : ''}
                      </div>
                    </div>
                  </div>
                  {stop.is_hub && (
                    <span className="text-[9px] font-medium px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 shrink-0">
                      Hub
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Controls Capsule */}
      <div className="flex items-center gap-1.5 pointer-events-auto">
        {/* Incident Alert */}
        <button
          onClick={onToggleIncident}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all shadow-sm backdrop-blur-xl border ${
            hasIncident
              ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-300 dark:border-rose-900 animate-pulse'
              : 'bg-white/90 dark:bg-zinc-900/90 text-zinc-600 dark:text-zinc-400 border-zinc-200/80 dark:border-zinc-800/80 hover:text-zinc-900 dark:hover:text-zinc-100'
          }`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${hasIncident ? 'bg-rose-500' : 'bg-emerald-500'}`}></span>
          <span>{hasIncident ? 'Aviso Retención' : 'Red Fluida'}</span>
        </button>

        {/* Peak/Off-peak */}
        <button
          onClick={onTogglePeak}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-white/90 dark:bg-zinc-900/90 text-zinc-600 dark:text-zinc-400 border border-zinc-200/80 dark:border-zinc-800/80 shadow-sm backdrop-blur-xl hover:text-zinc-900 dark:hover:text-zinc-100 transition-all"
        >
          <span className="text-[10px]">{isPeak ? '⚡ Punta' : '🌱 Valle'}</span>
        </button>

        {/* Live GTFS Count */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/90 dark:bg-zinc-900/90 text-zinc-700 dark:text-zinc-300 border border-zinc-200/80 dark:border-zinc-800/80 text-xs font-medium shadow-sm backdrop-blur-xl">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>4.771 GTFS</span>
        </div>
      </div>
    </div>
  );
}
