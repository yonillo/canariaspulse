import React from 'react';
import { Bus, Compass, Route, CreditCard, FlaskConical } from 'lucide-react';

export default function BottomNav({ activeTab = 'arrivals', onTabChange = () => {} }) {
  const tabs = [
    { id: 'arrivals', label: 'Paradas', icon: Bus },
    { id: 'lines', label: 'Rutas GTFS', icon: Route },
    { id: 'planner', label: 'Plan 95%', icon: Compass },
    { id: 'card', label: 'Bono 15', icon: CreditCard },
    { id: 'lab', label: 'Laboratorio', icon: FlaskConical },
  ];

  return (
    <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-[1000] w-auto max-w-[94vw] pointer-events-auto font-sans">
      <div className="flex items-center gap-1 p-1 rounded-full bg-white/85 dark:bg-zinc-900/85 backdrop-blur-2xl border border-zinc-200/70 dark:border-zinc-800/70 shadow-lg">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`relative flex items-center gap-1.5 px-3 py-1.5 sm:px-4 sm:py-2 rounded-full text-xs font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 shadow-sm'
                  : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-800/50'
              }`}
            >
              <Icon className="w-3.5 h-3.5 stroke-[1.8]" />
              <span className="hidden sm:inline tracking-tight">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
