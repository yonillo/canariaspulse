import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Filter, Layers, Navigation } from 'lucide-react';

export default function MapView({
  stops = [],
  vehicles = [],
  linesCatalog = [],
  selectedStop = null,
  onSelectStop = () => {},
  selectedLine = null,
  activeRouteGeometry = null,
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);
  const vehiclesLayerRef = useRef(null);
  const polylinesLayerRef = useRef(null);

  const [activeOperatorFilter, setActiveOperatorFilter] = useState('ALL');

  // Inicializar mapa con CartoDB Voyager (estética minimalista, clara y legible)
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [28.25, -15.85],
      zoom: 9,
      zoomControl: false,
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Tiles minimalistas CartoDB Voyager
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd',
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    mapInstanceRef.current = map;
    markersLayerRef.current = L.layerGroup().addTo(map);
    vehiclesLayerRef.current = L.layerGroup().addTo(map);
    polylinesLayerRef.current = L.layerGroup().addTo(map);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Dibujar trazados de transporte
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layer = polylinesLayerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    const filteredLines = linesCatalog.filter((line) => {
      if (activeOperatorFilter === 'ALL') return true;
      if (activeOperatorFilter === 'GLOBAL') return line.operator === 'GLOBAL' || (!line.operator && !line.line_id?.includes('TITSA'));
      if (activeOperatorFilter === 'TITSA') return line.operator === 'TITSA' || line.operator === 'METROTENERIFE';
      if (activeOperatorFilter === 'GUAGUAS_MUNICIPALES') return line.operator === 'GUAGUAS_MUNICIPALES';
      if (activeOperatorFilter === 'MARITIME') return line.operator === 'FRED_OLSEN' || line.operator === 'NAVIERA_ARMAS' || line.operator === 'BALEARIA';
      return true;
    });

    filteredLines.forEach((line) => {
      const isSelected = selectedLine === line.line_id;
      const opacity = selectedLine ? (isSelected ? 0.95 : 0.15) : 0.65;
      const weight = selectedLine && isSelected ? 5 : line.mode === 'maritime' ? 3.5 : 2.8;
      const color = line.color || '#00778b';
      const isDashed = line.mode === 'maritime' || line.is_express;

      if (line.polyline && line.polyline.length > 0) {
        const poly = L.polyline(line.polyline, {
          color: color,
          weight: weight,
          opacity: opacity,
          lineJoin: 'round',
          dashArray: isDashed ? '6, 6' : null,
        }).addTo(layer);

        poly.bindTooltip(
          `<div class="p-1 font-sans">
            <div class="text-[10px] font-semibold text-zinc-500">${line.operator || 'Canarias'}</div>
            <div class="font-bold text-xs text-zinc-900">${line.line_id} • ${line.name}</div>
            <div class="text-[10px] text-zinc-600">${line.corridor || ''}</div>
          </div>`,
          { sticky: true }
        );
      }
    });

    if (activeRouteGeometry && activeRouteGeometry.length > 0) {
      const activePoly = L.polyline(activeRouteGeometry, {
        color: '#f59e0b',
        weight: 6,
        opacity: 0.95,
      }).addTo(layer);
      map.fitBounds(activePoly.getBounds(), { padding: [50, 50] });
    }
  }, [linesCatalog, selectedLine, activeRouteGeometry, activeOperatorFilter]);

  // Dibujar paradas clave y puertos
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layer = markersLayerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    stops.forEach((stop) => {
      const isSelected = selectedStop && (selectedStop.id === stop.id || selectedStop.code === stop.code);
      const isMaritime = stop.id?.includes('PUERTO') || stop.id?.includes('TENERIFE') || stop.id?.includes('MORRO') || stop.id?.includes('PORT_');

      const iconHtml = `
        <div class="relative flex items-center justify-center cursor-pointer group">
          ${isSelected ? '<div class="absolute w-7 h-7 rounded-full bg-amber-400/40 animate-ping"></div>' : ''}
          <div class="w-5 h-5 rounded-full flex items-center justify-center shadow-md transition-all duration-150 transform group-hover:scale-125 ${
            isSelected
              ? 'bg-amber-500 text-zinc-950 border-2 border-white ring-2 ring-amber-400/50 font-bold'
              : isMaritime
              ? 'bg-sky-600 text-white border border-white'
              : stop.is_hub
              ? 'bg-zinc-900 text-amber-400 border border-amber-400 font-bold'
              : 'bg-zinc-800 text-white border border-white/60'
          }">
            <span style="font-size: 9px;">${isMaritime ? '⛴' : '•'}</span>
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        className: 'custom-stop-marker',
        html: iconHtml,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      });

      const marker = L.marker([stop.lat, stop.lon], { icon: customIcon }).addTo(layer);

      marker.on('click', () => {
        onSelectStop(stop);
        map.flyTo([stop.lat, stop.lon], 13, { duration: 1.0 });
      });

      marker.bindTooltip(
        `<div class="p-1 font-sans">
          <div class="font-bold text-zinc-900 text-xs">${stop.name}</div>
          <div class="text-[10px] text-zinc-500">${stop.locality || 'Canarias'}</div>
        </div>`,
        { direction: 'top', offset: [0, -8] }
      );
    });
  }, [stops, selectedStop, onSelectStop]);

  // Dibujar flota GPS en vivo
  useEffect(() => {
    const layer = vehiclesLayerRef.current;
    if (!layer) return;

    layer.clearLayers();

    const filteredVehicles = vehicles.filter((v) => {
      if (activeOperatorFilter === 'ALL') return true;
      if (activeOperatorFilter === 'GLOBAL') return v.operator === 'GLOBAL' || (!v.operator && !v.line?.toString().includes('TITSA'));
      if (activeOperatorFilter === 'TITSA') return v.operator === 'TITSA' || v.operator === 'METROTENERIFE';
      if (activeOperatorFilter === 'GUAGUAS_MUNICIPALES') return v.operator === 'GUAGUAS_MUNICIPALES';
      if (activeOperatorFilter === 'MARITIME') return v.operator === 'FRED_OLSEN' || v.operator === 'NAVIERA_ARMAS' || v.operator === 'BALEARIA';
      return true;
    });

    filteredVehicles.forEach((v) => {
      const isMaritime = v.mode === 'maritime';
      const isTitsa = v.operator === 'TITSA';
      const isTram = v.operator === 'METROTENERIFE';
      const isMunicipal = v.operator === 'GUAGUAS_MUNICIPALES';
      const isBalearia = v.operator === 'BALEARIA';

      const dotColor =
        v.occupancy_ratio > 0.85
          ? 'bg-rose-500'
          : v.occupancy_ratio > 0.5
          ? 'bg-amber-400'
          : 'bg-emerald-500';

      let markerHtml = '';

      if (isMaritime) {
        markerHtml = `
          <div class="relative flex items-center justify-center cursor-pointer transition-all hover:scale-105">
            <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-zinc-900/90 text-white border border-zinc-700/80 shadow-lg backdrop-blur-md">
              <span class="text-xs">${isBalearia ? '🛳️' : '⛴️'}</span>
              <span class="font-bold text-[10px] text-zinc-100">${v.label.split(' (')[0]}</span>
            </div>
          </div>
        `;
      } else {
        const lineAccent = isTram ? 'text-rose-400' : isTitsa ? 'text-lime-400' : isMunicipal ? 'text-amber-400' : 'text-cyan-400';
        markerHtml = `
          <div class="relative flex items-center justify-center cursor-pointer transition-all hover:scale-105">
            <div class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-zinc-900/90 text-white border border-zinc-700/80 shadow-lg backdrop-blur-sm">
              <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
              <span class="font-bold text-[11px] ${lineAccent}">${v.line_id || v.line}</span>
            </div>
          </div>
        `;
      }

      const customIcon = L.divIcon({
        className: 'custom-vehicle-marker',
        html: markerHtml,
        iconSize: isMaritime ? [110, 24] : [56, 22],
        iconAnchor: isMaritime ? [55, 12] : [28, 11],
      });

      const marker = L.marker([v.lat, v.lon], { icon: customIcon }).addTo(layer);

      marker.bindTooltip(
        `<div class="p-1 font-sans text-xs">
          <div class="font-bold text-zinc-900">${v.label}</div>
          <div class="text-zinc-600 text-[11px]">${v.operator_name || v.operator} • ${v.speed_kmh} km/h</div>
          <div class="text-zinc-500 text-[10px] mt-0.5">Destino: ${v.destination}</div>
        </div>`,
        { direction: 'top', offset: [0, -10] }
      );
    });
  }, [vehicles, activeOperatorFilter]);

  return (
    <div className="w-full h-full relative">
      <div ref={mapContainerRef} className="w-full h-full relative" />

      {/* Selector Flotante Minimalista de Operador */}
      <div className="absolute top-20 left-4 z-[800] flex items-center gap-1 p-1 rounded-full bg-white/85 dark:bg-zinc-900/85 backdrop-blur-xl border border-zinc-200/60 dark:border-zinc-800/80 shadow-md">
        <button
          onClick={() => setActiveOperatorFilter('ALL')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
            activeOperatorFilter === 'ALL'
              ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-sm'
              : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
          }`}
        >
          Todo
        </button>
        <button
          onClick={() => setActiveOperatorFilter('GLOBAL')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
            activeOperatorFilter === 'GLOBAL'
              ? 'bg-[#00778b] text-white shadow-sm'
              : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
          }`}
        >
          Global
        </button>
        <button
          onClick={() => setActiveOperatorFilter('TITSA')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
            activeOperatorFilter === 'TITSA'
              ? 'bg-lime-600 text-white shadow-sm'
              : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
          }`}
        >
          TITSA
        </button>
        <button
          onClick={() => setActiveOperatorFilter('GUAGUAS_MUNICIPALES')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
            activeOperatorFilter === 'GUAGUAS_MUNICIPALES'
              ? 'bg-amber-500 text-zinc-950 shadow-sm'
              : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
          }`}
        >
          Guaguas
        </button>
        <button
          onClick={() => setActiveOperatorFilter('MARITIME')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
            activeOperatorFilter === 'MARITIME'
              ? 'bg-sky-600 text-white shadow-sm'
              : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
          }`}
        >
          Marítimo
        </button>
      </div>
    </div>
  );
}
