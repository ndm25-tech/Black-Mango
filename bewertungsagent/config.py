"""Konfiguration: Umgebungsvariablen, Modellname, Lernphase-Schalter.

Liest Werte aus einer .env-Datei (siehe .env.example). Die Imports sind
absichtlich fehlertolerant, damit sich das Modul auch ohne installierte
Abhängigkeiten importieren lässt (z. B. für den Offline-Trockenlauf der Demo).
"""

import os

# python-dotenv ist optional beim reinen Import — nur für echte Läufe nötig.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - nur relevant vor "pip install"
    pass


def _als_bool(wert: str) -> bool:
    return str(wert).strip().lower() in ("1", "true", "yes", "ja", "on")


# Modellname mit Bindestrichen + Dezimalpunkt (z. B. "gemini-2.5-flash").
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Lernphase: solange True, muss JEDE Antwort vor Veröffentlichung freigegeben werden.
LERNPHASE = _als_bool(os.getenv("LERNPHASE", "true"))

# Few-Shot: so viele der besten (unveränderten) Antworten als Vorbild in den Prompt.
ANZAHL_FEWSHOT = int(os.getenv("ANZAHL_FEWSHOT", "3"))

# So viele Muster-Antworten aus der Stil-Bibliothek als Grund-Vorbild mitgeben.
ANZAHL_STIL_BIBLIOTHEK = int(os.getenv("ANZAHL_STIL_BIBLIOTHEK", "3"))

# Kreativität des Modells (0 = immer gleich/steif, ~1 = abwechslungsreich/natürlich).
# Höher = "Neu generieren" bringt echte Varianten und der Ton klingt menschlicher.
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))


def pruefe_api_key() -> None:
    """Wirft einen klaren Fehler, wenn der API-Key fehlt."""
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY fehlt. Lege eine .env-Datei an "
            "(cp .env.example .env) und trage deinen Google-API-Key ein."
        )
