#!/bin/bash
# Startet das Kudora-Backend (api.py) zuverlässig in EINEM Befehl:
#   bash start-api.sh
# Legt bei Bedarf die Python-Umgebung (.venv) an, installiert fehlende Pakete,
# prüft den GOOGLE_API_KEY und startet dann den Server auf http://localhost:8000.
# So können "command not found" oder "no such file or directory" nicht mehr passieren.

cd "$(dirname "$0")" || exit 1

# 1) Virtuelle Umgebung sicherstellen (anlegen, falls sie fehlt).
if [ ! -d ".venv" ]; then
  echo "→ Lege virtuelle Umgebung (.venv) an ..."
  python3 -m venv .venv || { echo "Konnte .venv nicht anlegen. Ist Python 3 installiert?"; exit 1; }
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# 2) Abhängigkeiten nur installieren, wenn FastAPI/uvicorn fehlen.
if ! python -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "→ Installiere Abhängigkeiten (einmalig) ..."
  pip install -r requirements.txt
fi

# 3) GOOGLE_API_KEY prüfen (aus Umgebung ODER .env) — nur ein freundlicher Hinweis.
python - <<'PY'
import os
key = os.getenv("GOOGLE_API_KEY")
if not key and os.path.exists(".env"):
    for zeile in open(".env", encoding="utf-8"):
        z = zeile.strip()
        if z.startswith("GOOGLE_API_KEY") and "=" in z:
            key = z.split("=", 1)[1].strip().strip('"').strip("'")
            break
if key:
    print("✓ GOOGLE_API_KEY gefunden.")
else:
    print("⚠  GOOGLE_API_KEY fehlt — trage ihn in die .env ein (derselbe wie bei der App).")
    print("   Der Server startet trotzdem; Antworten kommen erst mit gültigem Schlüssel.")
PY

# 4) Server starten.
echo "→ Starte Kudora-Backend auf http://localhost:8000  (Stoppen mit Strg+C)"
exec uvicorn api:app --port 8000
