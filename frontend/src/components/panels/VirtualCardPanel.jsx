import React, { useState, useEffect } from 'react';
import { CreditCard, QrCode, CheckCircle2, Wifi, Sparkles, ChevronRight } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function VirtualCardPanel() {
  const [trips, setTrips] = useState(11);
  const [showQR, setShowQR] = useState(false);

  const goal = 15;
  const remaining = Math.max(0, goal - trips);
  const isGoalReached = trips >= goal;
  const percent = Math.min(100, Math.round((trips / goal) * 100));

  const handleValidate = () => {
    const next = trips + 1;
    setTrips(next);
    if (next >= goal) {
      try {
        confetti({
          particleCount: 80,
          spread: 60,
          origin: { y: 0.6 },
          colors: ['#10b981', '#f59e0b', '#3b82f6'],
        });
      } catch (e) {}
    }
  };

  return (
    <div className="flex flex-col h-full bg-white/90 dark:bg-zinc-900/90 text-zinc-900 dark:text-zinc-100 backdrop-blur-2xl rounded-3xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-xl overflow-hidden font-sans">
      {/* Top Handle */}
      <div className="w-8 h-1 rounded-full bg-zinc-300 dark:bg-zinc-700 mx-auto mt-2.5"></div>

      {/* Header */}
      <div className="p-4 border-b border-zinc-100 dark:border-zinc-800/80">
        <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">Bono Residente Canario</h2>
        <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5">Control de gratuidad mensual (regla 15 viajes)</p>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {/* Apple Wallet Style Pass */}
        <div className="relative p-5 rounded-3xl bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-950 text-white shadow-2xl overflow-hidden border border-zinc-700/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center font-bold text-xs text-amber-400">
                ✦
              </span>
              <span className="text-xs font-semibold tracking-wider uppercase text-zinc-300">Gobierno de Canarias</span>
            </div>
            <Wifi className="w-4 h-4 text-zinc-400 rotate-90" />
          </div>

          <div className="my-6">
            <div className="text-[10px] uppercase font-bold text-zinc-400 tracking-wider">Titular de la tarjeta</div>
            <div className="text-lg font-black tracking-tight text-white mt-0.5">ALEXANDER D. H.</div>
            <div className="text-[11px] text-zinc-400 mt-0.5 font-mono">ES-GC-35002 • WAWA JOVEN</div>
          </div>

          <div className="flex items-end justify-between pt-3 border-t border-white/10">
            <div>
              <div className="text-[10px] text-zinc-400 uppercase font-semibold">Viajes este mes</div>
              <div className="text-2xl font-black text-amber-400 tabular-nums">
                {trips} <span className="text-sm font-normal text-zinc-400">/ 15</span>
              </div>
            </div>

            <div className="text-right">
              <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                isGoalReached ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
              }`}>
                {isGoalReached ? 'Gratis el mes que viene' : `${remaining} restantes`}
              </span>
            </div>
          </div>
        </div>

        {/* Progress Bar Card */}
        <div className="p-3.5 rounded-2xl bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-100 dark:border-zinc-800/60 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-zinc-600 dark:text-zinc-400">Progreso de Gratuidad</span>
            <span className="tabular-nums text-zinc-900 dark:text-zinc-100">{percent}%</span>
          </div>

          <div className="w-full h-2 rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden">
            <div
              className="h-full rounded-full bg-zinc-900 dark:bg-zinc-100 transition-all duration-300"
              style={{ width: `${percent}%` }}
            ></div>
          </div>

          <div className="text-[11px] text-zinc-500 dark:text-zinc-400 pt-0.5">
            {isGoalReached
              ? 'Has alcanzado los 15 viajes requeridos por el Cabildo. Tu bono se renovará al 100% subvencionado el día 1.'
              : `Realiza ${remaining} viaje${remaining > 1 ? 's' : ''} más en los próximos 12 días para no perder la gratuidad.`}
          </div>
        </div>

        {/* Action Button */}
        <div className="space-y-2">
          <button
            onClick={handleValidate}
            className="w-full py-2.5 rounded-2xl bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 font-semibold text-xs hover:opacity-90 transition-all shadow-sm flex items-center justify-center gap-2"
          >
            <CreditCard className="w-4 h-4" />
            <span>Simular Validación NFC en Guagua / Ferry (+1)</span>
          </button>

          <button
            onClick={() => setShowQR(!showQR)}
            className="w-full py-2 rounded-2xl bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-medium text-xs hover:bg-zinc-200 dark:hover:bg-zinc-700/60 transition-all flex items-center justify-center gap-1.5"
          >
            <QrCode className="w-3.5 h-3.5" />
            <span>{showQR ? 'Ocultar código QR' : 'Mostrar código QR para validadora'}</span>
          </button>
        </div>

        {showQR && (
          <div className="p-4 rounded-2xl bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 flex flex-col items-center">
            <div className="w-36 h-36 bg-zinc-950 p-2 rounded-xl flex items-center justify-center text-white text-[10px] text-center">
              [CÓDIGO QR SEGURO MAAS CANARIAS]
            </div>
            <div className="text-[10px] text-zinc-400 mt-2 font-mono">TOKEN: GC-VAL-9281-CANARIAS</div>
          </div>
        )}
      </div>
    </div>
  );
}
