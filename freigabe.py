"""Freigabe-Schritt: Mensch prüft jeden Entwurf, Ergebnis geht ins Gedächtnis.

Aufruf:
  python freigabe.py            # echte Entwürfe via Gemini (braucht GOOGLE_API_KEY)
  python freigabe.py --offline  # Platzhalter-Entwürfe, ohne API-Key testbar

Pro Bewertung:
  1. Bewertung + KI-Entwurf anzeigen
  2. ENTER  -> Entwurf so übernehmen
     Text   -> deine Korrektur wird die finale Antwort
  3. Alles (Original, Entwurf, finale Antwort, "geändert?") wird gespeichert.

Hinweis für später: `verarbeite_bewertung()` nimmt eine Bewertung als einfaches
dict (betrieb/sterne/text). Genau so kommt später der Zapier-Webhook rein — dann
tauscht man nur die Beispiel-Liste gegen den echten Google-Input aus.
"""

import sys

from bewertungsagent import agent, protokoll
from bewertungsagent.beispiele import BEISPIEL_BEWERTUNGEN


def _entwurf_holen(betrieb: str, text: str, sterne: int, offline: bool) -> str:
    if offline:
        return f"[Offline-Platzhalter — hier stünde der Gemini-Entwurf für {betrieb}]"
    return agent.antwort_erzeugen(betrieb, text, sterne)["entwurf"]


def _eingabe(prompt: str) -> str:
    """input(), das bei Ende der Eingabe (EOF) einfach 'übernehmen' bedeutet."""
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def verarbeite_bewertung(bewertung: dict, offline: bool = False) -> dict:
    """Zeigt eine Bewertung + Entwurf, holt die Freigabe, speichert das Ergebnis."""
    betrieb = bewertung["betrieb"]
    sterne = bewertung["sterne"]
    text = bewertung["text"]

    entwurf = _entwurf_holen(betrieb, text, sterne, offline)

    print(f"Betrieb:  {betrieb}  ({sterne}/5 Sterne)")
    print(f'Bewertung: "{text}"')
    print(f"Entwurf:  {entwurf}")

    eingabe = _eingabe("[ENTER = übernehmen | oder Korrektur eintippen]: ")
    finale_antwort = entwurf if eingabe == "" else eingabe

    zeile = protokoll.speichere(betrieb, sterne, text, entwurf, finale_antwort)
    print(f"-> gespeichert (geändert: {zeile['geaendert']})")
    print("-" * 70)
    return zeile


def main() -> None:
    offline = "--offline" in sys.argv[1:]
    print(f"Freigabe-Lauf  (Modus: {'OFFLINE' if offline else 'ECHT/Gemini'})")
    print(f"Gespeichert wird nach: {protokoll.CSV_PFAD}")
    print("=" * 70)

    for bewertung in BEISPIEL_BEWERTUNGEN:
        verarbeite_bewertung(bewertung, offline=offline)

    gesamt = protokoll.lade_alle()
    print(f"Protokoll enthält jetzt {len(gesamt)} Einträge.")


if __name__ == "__main__":
    main()
