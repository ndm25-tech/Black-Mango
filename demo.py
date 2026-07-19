"""Demo: erzeugt für jede Beispiel-Bewertung einen Entwurf + Freigabe-Status.

Aufruf:
  python demo.py            # echte Entwürfe via Gemini (braucht GOOGLE_API_KEY in .env)
  python demo.py --offline  # Trockenlauf ohne LLM: zeigt nur Freigabe-Logik/Risikowörter

Der Offline-Modus ist praktisch, um die Struktur und die Freigabe-Regeln zu
prüfen, bevor ein API-Key hinterlegt ist.
"""

import sys

from bewertungsagent import agent
from bewertungsagent import config
from bewertungsagent.beispiele import BEISPIEL_BEWERTUNGEN


def _trenner() -> None:
    print("=" * 70)


def main() -> None:
    offline = "--offline" in sys.argv[1:]

    print(f"Modell: {config.MODEL_NAME}   Lernphase: {config.LERNPHASE}   "
          f"Modus: {'OFFLINE (kein LLM)' if offline else 'ECHT (Gemini)'}")
    _trenner()

    for i, bewertung in enumerate(BEISPIEL_BEWERTUNGEN, start=1):
        betrieb = bewertung["betrieb"]
        sterne = bewertung["sterne"]
        text = bewertung["text"]

        print(f"[{i}/{len(BEISPIEL_BEWERTUNGEN)}] {betrieb}  —  {sterne}/5 Sterne")
        print(f'Bewertung: "{text}"')

        freigabe = agent.braucht_freigabe(text, sterne)
        risiko = agent.gefundene_risikowoerter(text)

        if offline:
            print("Entwurf:   (Offline-Modus — hier würde der Gemini-Entwurf stehen)")
        else:
            ergebnis = agent.antwort_erzeugen(betrieb, text, sterne)
            freigabe = ergebnis["freigabe_noetig"]
            risiko = ergebnis["risikowoerter"]
            print(f"Entwurf:   {ergebnis['entwurf']}")

        status = "🔒 FREIGABE NÖTIG" if freigabe else "✅ darf direkt raus"
        print(f"Status:    {status}")
        if risiko:
            print(f"Risiko:    Signalwörter erkannt -> {', '.join(risiko)}")
        _trenner()


if __name__ == "__main__":
    main()
