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


def _hole(name: str, standard: str = "") -> str:
    """Liest eine Einstellung: erst .env/Umgebung (lokal), dann Streamlit-Secrets (Cloud).

    Auf Streamlit Cloud gibt es keine .env — dort trägt man die Werte unter
    "Secrets" ein. Der st.secrets-Zugriff ist geschützt, damit die CLI-Skripte
    (demo.py, freigabe.py) ohne Streamlit-Kontext weiter funktionieren.
    """
    wert = os.getenv(name)
    if wert is not None and wert != "":
        return wert
    try:
        import streamlit as st

        return str(st.secrets.get(name, standard))
    except Exception:  # noqa: BLE001 - kein Streamlit / keine Secrets -> Standard
        return standard


# Modellname mit Bindestrichen + Dezimalpunkt (z. B. "gemini-2.5-flash-lite").
# "lite" ist leichter/günstiger und hat ein separates Gratis-Tageskontingent.
MODEL_NAME = _hole("MODEL_NAME", "gemini-2.5-flash-lite")

GOOGLE_API_KEY = _hole("GOOGLE_API_KEY") or None

# Lernphase: solange True, muss JEDE Antwort vor Veröffentlichung freigegeben werden.
LERNPHASE = _als_bool(_hole("LERNPHASE", "true"))

# Few-Shot: so viele der besten Antworten als Vorbild in den Prompt.
ANZAHL_FEWSHOT = int(_hole("ANZAHL_FEWSHOT", "3"))

# So viele Muster-Antworten aus der Stil-Bibliothek als Grund-Vorbild mitgeben.
ANZAHL_STIL_BIBLIOTHEK = int(_hole("ANZAHL_STIL_BIBLIOTHEK", "3"))

# Kreativität des Modells (0 = immer gleich/steif, ~1 = abwechslungsreich/natürlich).
TEMPERATURE = float(_hole("TEMPERATURE", "0.85"))

# Passwort für den geheimen Entwickler-Bereich der App (nur für den Betreiber).
# Leer lassen = der Entwickler-Bereich ist komplett deaktiviert.
ENTWICKLER_PASSWORT = _hole("ENTWICKLER_PASSWORT", "")


def pruefe_api_key() -> None:
    """Wirft einen klaren Fehler, wenn der API-Key fehlt."""
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY fehlt. Lege eine .env-Datei an "
            "(cp .env.example .env) und trage deinen Google-API-Key ein."
        )
