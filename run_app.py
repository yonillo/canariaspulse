"""Script unificado de lanzamiento de Global Móvil 2.0.

Inicia el servidor FastAPI sirviendo la aplicación React + Tailwind a pantalla completa
y abre automáticamente el navegador en http://localhost:8000.
"""

from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn

def open_browser():
    time.sleep(1.2)
    print("\n[INFO] Abriendo Global Móvil 2.0 en el navegador: http://localhost:8000")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 75)
    print("   🚌 GLOBAL MÓVIL 2.0 | GRAN CANARIA SMART TRANSIT SYSTEM")
    print("=" * 75)
    print("  • Frontend: React 19 + Tailwind CSS v4 + Leaflet 60 FPS (Citymapper Feel)")
    print("  • Backend:  FastAPI + Inferencia Bayesiana + Optimización Operativa")
    print("  • Acceso:   http://localhost:8000")
    print("  • API Docs: http://localhost:8000/docs")
    print("=" * 75)

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, log_level="info")
