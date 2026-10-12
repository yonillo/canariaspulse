import React, { useState, useEffect } from 'react';
import MapView from './components/MapView';
import TopNavigation from './components/TopNavigation';
import BottomNav from './components/BottomNav';
import ArrivalsPanel from './components/panels/ArrivalsPanel';
import PlannerPanel from './components/panels/PlannerPanel';
import LinesPanel from './components/panels/LinesPanel';
import VirtualCardPanel from './components/panels/VirtualCardPanel';
import LabPanel from './components/panels/LabPanel';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function App() {
  const [networkData, setNetworkData] = useState({
    hubs: {},
    official_stops: [],
    lines_catalog: [],
    highway_polylines: {},
    gtfs_summary: null,
  });
  const [fleetVehicles, setFleetVehicles] = useState([]);
  const [selectedStop, setSelectedStop] = useState(null);
  const [selectedLine, setSelectedLine] = useState(null);
  const [activeTab, setActiveTab] = useState('arrivals');
  const [hasIncident, setHasIncident] = useState(false);
  const [isPeak, setIsPeak] = useState(true);
  const [isDrawerOpen, setIsDrawerOpen] = useState(true);

  // Cargar datos de red al montar
  useEffect(() => {
    fetch('/api/network/overview')
      .then((res) => res.json())
      .then((data) => {
        setNetworkData(data);
        if (data.official_stops && data.official_stops.length > 0) {
          setSelectedStop(data.official_stops[0]);
        }
      })
      .catch((err) => console.error('Error al cargar red:', err));
  }, []);

  // Polling de flota GPS cada 4 segundos
  useEffect(() => {
    const fetchFleet = () => {
      fetch('/api/fleet/live')
        .then((res) => res.json())
        .then((data) => setFleetVehicles(data.vehicles || []))
        .catch(() => {});
    };

    fetchFleet();
    const interval = setInterval(fetchFleet, 4000);
    return () => clearInterval(interval);
  }, []);

  // Manejar selección de parada desde el buscador
  const handleSearchSelect = (stop) => {
    setSelectedStop(stop);
    setActiveTab('arrivals');
    setIsDrawerOpen(true);
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-zinc-100 dark:bg-zinc-950 select-none font-sans">
      {/* 1. MAPA INTERACTIVO A PANTALLA COMPLETA */}
      <div className="absolute inset-0 z-0">
        <MapView
          stops={networkData.official_stops}
          vehicles={fleetVehicles}
          linesCatalog={networkData.lines_catalog}
          selectedStop={selectedStop}
          onSelectStop={(stop) => {
            setSelectedStop(stop);
            setActiveTab('arrivals');
            setIsDrawerOpen(true);
          }}
          selectedLine={selectedLine}
        />
      </div>

      {/* 2. BARRA DE NAVEGACIÓN SUPERIOR FLOTANTE */}
      <TopNavigation
        onSearchSelect={handleSearchSelect}
        hasIncident={hasIncident}
        onToggleIncident={() => setHasIncident(!hasIncident)}
        isPeak={isPeak}
        onTogglePeak={() => setIsPeak(!isPeak)}
        vehiclesCount={fleetVehicles.length}
        gtfsSummary={networkData.gtfs_summary}
      />

      {/* 3. PANEL LATERAL / DRAWER FLOTANTE MINIMALISTA */}
      <div
        className={`absolute z-[900] transition-all duration-300 ease-out ${
          isDrawerOpen
            ? 'bottom-20 left-4 right-4 md:right-auto md:bottom-24 md:left-6 md:w-[390px] md:h-[calc(100vh-140px)] h-[56vh]'
            : 'bottom-20 left-4 md:left-6 w-auto h-auto'
        }`}
      >
        {isDrawerOpen ? (
          <div className="relative w-full h-full flex flex-col">
            {/* Botón de minimizar drawer */}
            <button
              onClick={() => setIsDrawerOpen(false)}
              className="absolute -top-3 right-4 z-50 p-1 rounded-full bg-white dark:bg-zinc-800 text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 border border-zinc-200 dark:border-zinc-700 shadow-md transition-all"
              title="Minimizar panel"
            >
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {activeTab === 'arrivals' && (
              <ArrivalsPanel
                selectedStop={selectedStop}
                onSelectStop={setSelectedStop}
                hubs={networkData.hubs}
                hasIncident={hasIncident}
                isPeak={isPeak}
              />
            )}

            {activeTab === 'lines' && (
              <LinesPanel
                lines={networkData.lines_catalog}
                selectedLine={selectedLine}
                onSelectLine={setSelectedLine}
              />
            )}

            {activeTab === 'planner' && (
              <PlannerPanel
                hubs={networkData.hubs}
                hasIncident={hasIncident}
                isPeak={isPeak}
              />
            )}

            {activeTab === 'card' && <VirtualCardPanel />}

            {activeTab === 'lab' && <LabPanel />}
          </div>
        ) : (
          <button
            onClick={() => setIsDrawerOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-white/90 dark:bg-zinc-900/90 text-zinc-800 dark:text-zinc-200 font-medium text-xs border border-zinc-200 dark:border-zinc-800 shadow-lg backdrop-blur-xl hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-all"
          >
            <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />
            <span>Abrir {activeTab === 'arrivals' ? 'Paradas' : activeTab === 'lines' ? 'Líneas' : activeTab === 'planner' ? 'Plan 95%' : activeTab === 'card' ? 'Bono' : 'Laboratorio'}</span>
          </button>
        )}
      </div>

      {/* 4. BARRA DE PESTAÑAS INFERIOR FLOTANTE (DOCK) */}
      <BottomNav
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab);
          setIsDrawerOpen(true);
        }}
      />
    </div>
  );
}
