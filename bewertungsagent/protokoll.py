"""Das Gedächtnis des Agenten: speichert und lädt das Lern-Protokoll.

Für jede Bewertung merken wir uns:
  Original + KI-Entwurf + finale (freigegebene) Antwort + "wurde geändert?"

Wichtig zum Verständnis: Das ist KEIN echtes Training. Das Modell lernt nicht.
Wir bauen hier ein "Gedächtnis im Code" — eine einfache CSV-Datei. Aus den
gesammelten Beispielen zieht Woche 3 dann die besten Antworten und gibt sie als
Vorbild (Few-Shot) in den Prompt. Das ist "die KI lernt deinen Stil".

Wir nutzen nur Pythons Standardbibliothek (csv, pathlib, datetime) — keine neue
Abhängigkeit nötig.
"""

import csv
from datetime import datetime
from pathlib import Path

# Pfad: <Projekt-Root>/daten/protokoll.csv  (daten/ ist per .gitignore ausgenommen,
# weil Kundendaten nicht ins Repo gehören -> DSGVO).
PROJEKT_ROOT = Path(__file__).resolve().parent.parent
DATEN_DIR = PROJEKT_ROOT / "daten"
CSV_PFAD = DATEN_DIR / "protokoll.csv"

SPALTEN = [
    "zeitstempel",
    "betrieb",
    "sterne",
    "original",
    "entwurf",
    "finale_antwort",
    "geaendert",
]


def speichere(betrieb: str, sterne: int, original: str,
              entwurf: str, finale_antwort: str) -> dict:
    """Hängt eine Zeile ans Protokoll an und gibt sie zurück.

    Legt Ordner + Datei + Kopfzeile automatisch an, falls noch nicht vorhanden.
    'geaendert' wird berechnet: 'ja', wenn der Mensch den Entwurf verändert hat.
    """
    geaendert = "ja" if (entwurf or "").strip() != (finale_antwort or "").strip() else "nein"

    zeile = {
        "zeitstempel": datetime.now().isoformat(timespec="seconds"),
        "betrieb": betrieb,
        "sterne": sterne,
        "original": original,
        "entwurf": entwurf,
        "finale_antwort": finale_antwort,
        "geaendert": geaendert,
    }

    DATEN_DIR.mkdir(parents=True, exist_ok=True)
    datei_ist_neu = not CSV_PFAD.exists()
    with CSV_PFAD.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SPALTEN)
        if datei_ist_neu:
            writer.writeheader()
        writer.writerow(zeile)

    return zeile


def lade_alle() -> list[dict]:
    """Liest alle gespeicherten Zeilen zurück (leer, wenn noch nichts da ist)."""
    if not CSV_PFAD.exists():
        return []
    with CSV_PFAD.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def beste_beispiele(n: int = 3) -> list[dict]:
    """Vorbereitung Woche 3: unveränderte Entwürfe = gute Vorbilder (Few-Shot).

    Wenn der Mensch einen Entwurf NICHT ändern musste, war er gut. Genau solche
    Beispiele wollen wir später in den Prompt geben. Hier nur eingesammelt.
    """
    gute = [z for z in lade_alle() if z.get("geaendert") == "nein"]
    return gute[-n:]  # die n neuesten guten Beispiele
