#!/bin/bash
# Startet die Bewertungs-Agent-App zuverlässig in EINEM Befehl:
#   bash start.sh
# Wechselt ins Projekt, aktiviert die Python-Umgebung (.venv) und startet Streamlit.
# So kann "command not found" (venv nicht aktiv) nicht mehr passieren.

cd "$(dirname "$0")" || exit 1

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  echo "Hinweis: keine .venv gefunden. Erst einrichten mit:"
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

exec streamlit run app.py
