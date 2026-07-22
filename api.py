"""Kudora-Backend-API für die Chrome-Erweiterung.

Warum es das gibt: Die Chrome-Erweiterung darf den Gemini-Schlüssel NICHT
enthalten (ihr Code ist im Browser lesbar). Deshalb ruft die Erweiterung diesen
kleinen Server auf, der den Schlüssel server-seitig hält und die BESTEHENDE
Agent-Logik wiederverwendet (`bewertungsagent.agent` / `.protokoll`) — kein
Prompt und keine Regel wird hier dupliziert.

Endpunkte:
  GET  /                 -> Health-Check (läuft der Server?)
  POST /api/antwort      -> {original, sterne, betrieb} -> Antwort-Entwurf
  POST /api/freigabe     -> freigegebene Antwort speichern (Lern-Kreislauf)

Start (lokal):
  uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from bewertungsagent import agent, protokoll
from bewertungsagent.agent import TageslimitErreicht

app = FastAPI(title="Kudora API", version="1.0.0")

# CORS: Chrome-Erweiterungen senden einen Origin wie "chrome-extension://<id>".
# Für den Test breit erlauben; später auf die feste Erweiterungs-ID eingrenzen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class AntwortAnfrage(BaseModel):
    original: str = Field(..., description="Der Bewertungstext des Gastes.")
    sterne: int = Field(5, ge=1, le=5, description="Sternzahl 1-5.")
    betrieb: str = Field("", description="Optionaler Name des Betriebs.")


class FreigabeAnfrage(BaseModel):
    original: str
    sterne: int = Field(5, ge=1, le=5)
    betrieb: str = ""
    entwurf: str = Field("", description="Der ursprüngliche KI-Entwurf.")
    finale_antwort: str = Field(..., description="Die tatsächlich veröffentlichte Antwort.")


@app.get("/")
def health() -> dict:
    """Einfacher Health-Check + welches Modell gerade aktiv ist."""
    return {"status": "ok", "modell": agent.aktives_modell()}


@app.post("/api/antwort")
def antwort(anfrage: AntwortAnfrage) -> dict:
    """Erzeugt einen Antwort-Entwurf für eine Bewertung (nutzt Stil-Lernen)."""
    try:
        ergebnis = agent.antwort_erzeugen(
            anfrage.betrieb, anfrage.original, anfrage.sterne
        )
        return {"ok": True, **ergebnis}
    except TageslimitErreicht as fehler:
        return {"ok": False, "fehler": "tageslimit", "meldung": str(fehler)}
    except RuntimeError as fehler:
        # z. B. fehlender API-Key oder kein verfügbares Modell.
        return {"ok": False, "fehler": "konfiguration", "meldung": str(fehler)}
    except Exception as fehler:  # noqa: BLE001 - für die Erweiterung sauber zurückgeben
        return {"ok": False, "fehler": "unbekannt", "meldung": str(fehler)}


@app.post("/api/freigabe")
def freigabe(anfrage: FreigabeAnfrage) -> dict:
    """Speichert eine freigegebene Antwort -> Agent lernt den Stil fürs nächste Mal."""
    zeile = protokoll.speichere(
        betrieb=anfrage.betrieb,
        sterne=anfrage.sterne,
        original=anfrage.original,
        entwurf=anfrage.entwurf,
        finale_antwort=anfrage.finale_antwort,
    )
    return {"ok": True, "gespeichert": zeile}
