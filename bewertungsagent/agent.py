"""Kern des Agenten: Antwort-Entwurf erzeugen + Freigabe-Logik.

- SYSTEM_PROMPT bündelt die harten Rechts-/Sicherheitsregeln.
- braucht_freigabe() entscheidet, ob ein Mensch drüberschauen muss.
  In der Lernphase (config.LERNPHASE) ist das IMMER True.

Der LLM-Import passiert bewusst erst beim ersten echten Aufruf (lazy),
damit sich das Modul ohne installiertes langchain importieren lässt.
"""

import random
import time

from . import config, protokoll, stil_bibliothek


class TageslimitErreicht(RuntimeError):
    """Das kostenlose Tageskontingent des Modells ist aufgebraucht (429 PerDay)."""

SYSTEM_PROMPT = """
Du beantwortest Google-Bewertungen für einen Gastronomie- oder Hotelbetrieb in
Deutschland. Schreib so, wie es der Inhaber selbst tun würde: warm, echt und
persönlich. Man soll NICHT merken, dass eine KI antwortet.

SO KLINGT ES MENSCHLICH:
- Geh konkret auf das ein, was in der Bewertung wirklich steht — keine Floskeln.
- Fang NICHT jede Antwort mit "Vielen Dank" an; variiere den Einstieg.
- Kurz halten: 2 bis 3 Sätze. Kein langes, gestelztes Ende, kein "bla bla".
- Lockere, natürliche Sprache; ruhig etwas Persönlichkeit und echte Freude zeigen.
- Wenn dir Beispiel-Antworten gezeigt werden: übernimm ihren TON, aber kopiere die
  Formulierungen NICHT wörtlich — variiere besonders den ersten Satz.

FESTE REGELN (immer einhalten):
- Immer Sie-Form. Echte Umlaute (ä, ö, ü, ß). Keine Ausrufezeichen-Flut.
- Bei Kritik: ruhig, sachlich, deeskalierend, eher kurz (3 bis 4 Sätze). Höchstens
  einmal kurz Bedauern.
- Nichts erfinden, nichts versprechen (keine Gutscheine, Rabatte, Zusagen).
- Bei unbelegbaren Vorwürfen (z. B. "ihr seid Diebe") NICHT gegenkontern und NICHT
  streiten. Ruhig bleiben, Überraschung/Bedauern zeigen und um direkten Kontakt zur
  Klärung bitten.
- NIEMALS einen Namen nennen — auch nicht, wenn die Bewertung oder ein Beispiel einen
  nennt. Sag stattdessen "unser Team" oder "unsere Kollegin/unser Kollege".
- Keine Werbung.

Gib NUR die fertige Antwort aus, ohne Vorrede und ohne Anführungszeichen.
""".strip()

# Signalwörter, die auch bei guter Sternzahl eine menschliche Freigabe erzwingen.
RISIKO_WOERTER = [
    "lüge", "gelogen", "betrug", "abzocke", "abzocker", "dieb", "diebe",
    "diebstahl", "anzeige", "anwalt", "gesundheitsamt", "vergiftung",
    "rassist", "rassistisch", "beleidigt", "beleidigung", "geklaut",
]

_llm = None


def _get_llm():
    """Initialisiert das Gemini-Modell lazy (erst beim ersten echten Aufruf)."""
    global _llm
    if _llm is None:
        from langchain.chat_models import init_chat_model

        config.pruefe_api_key()
        _llm = init_chat_model(
            config.MODEL_NAME,
            model_provider="google_genai",
            temperature=config.TEMPERATURE,
        )
    return _llm


def _invoke_mit_retry(nachrichten: list[dict], versuche: int = 3):
    """Ruft das Modell auf und geht mit Rate-Limits (429) sinnvoll um.

    - Tageslimit (Meldung enthält "PerDay") -> sofort TageslimitErreicht, kein Retry
      (das Kontingent kommt erst am nächsten Tag zurück).
    - Kurzzeitiges Limit (pro Minute) -> kurz warten und erneut versuchen.
    """
    letzter_fehler = None
    for versuch in range(versuche):
        try:
            return _get_llm().invoke(nachrichten)
        except Exception as fehler:  # noqa: BLE001 - Fehlermeldung wird ausgewertet
            letzter_fehler = fehler
            text = str(fehler)
            ist_limit = "429" in text or "RESOURCE_EXHAUSTED" in text.upper()
            if not ist_limit:
                raise
            if "PerDay" in text:
                raise TageslimitErreicht(
                    "Das kostenlose Tageslimit dieses Modells ist erreicht. "
                    "Wechsle MODEL_NAME in der .env (z. B. gemini-2.5-flash) "
                    "oder versuche es morgen wieder."
                ) from fehler
            # Kurzzeitiges Limit: kurz warten und noch einmal versuchen.
            if versuch < versuche - 1:
                time.sleep(8)
    raise letzter_fehler


def gefundene_risikowoerter(review_text: str) -> list[str]:
    """Gibt die im Text gefundenen Risiko-Signalwörter zurück (für Transparenz)."""
    text = (review_text or "").lower()
    return [wort for wort in RISIKO_WOERTER if wort in text]


def braucht_freigabe(review_text: str, sterne: int) -> bool:
    """True, wenn ein Mensch die Antwort vor Veröffentlichung prüfen muss."""
    if config.LERNPHASE:
        return True
    if sterne < 5:
        return True
    return bool(gefundene_risikowoerter(review_text))


def _baue_user_nachricht(betrieb: str, review_text: str, sterne) -> str:
    return (
        f"Betrieb: {betrieb}\n"
        f"Sterne: {sterne} von 5\n"
        f'Bewertungstext: "{review_text}"\n\n'
        "Schreibe die Antwort."
    )


def baue_nachrichten(betrieb: str, review_text: str, sterne: int) -> list[dict]:
    """Baut die Nachrichten für Gemini — inklusive Few-Shot aus dem Gedächtnis.

    Few-Shot = "die KI lernt deinen Stil": frühere, von dir freigegebene und
    NICHT geänderte Antworten werden als Vorbild mitgeschickt. Das Modell selbst
    ändert sich nicht — es sieht nur gute Beispiele und ahmt den Ton nach.
    """
    nachrichten = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Grund-Vorbilder aus der Stil-Bibliothek — zufällige Auswahl sorgt für Abwechslung
    # (verschiedene Muster je Aufruf → "Neu generieren" fühlt sich frischer an).
    bibliothek = stil_bibliothek.STIL_BEISPIELE
    anzahl_bib = min(config.ANZAHL_STIL_BIBLIOTHEK, len(bibliothek))
    for bsp in random.sample(bibliothek, anzahl_bib):
        nachrichten.append({
            "role": "user",
            "content": _baue_user_nachricht(
                bsp.get("betrieb", ""), bsp.get("original", ""), bsp.get("sterne", ""),
            ),
        })
        nachrichten.append({"role": "assistant", "content": bsp.get("finale_antwort", "")})

    # Gedächtnis: die besten bisherigen Antworten als persönliches Vorbild.
    for bsp in protokoll.beste_beispiele(n=config.ANZAHL_FEWSHOT):
        nachrichten.append({
            "role": "user",
            "content": _baue_user_nachricht(
                bsp.get("betrieb", ""), bsp.get("original", ""), bsp.get("sterne", ""),
            ),
        })
        nachrichten.append({"role": "assistant", "content": bsp.get("finale_antwort", "")})

    # Zum Schluss die aktuelle Bewertung, die beantwortet werden soll.
    nachrichten.append({
        "role": "user",
        "content": _baue_user_nachricht(betrieb, review_text, sterne),
    })
    return nachrichten


def antwort_erzeugen(betrieb: str, review_text: str, sterne: int) -> dict:
    """Erzeugt einen Antwort-Entwurf (mit Few-Shot) und den Freigabe-Status."""
    nachrichten = baue_nachrichten(betrieb, review_text, sterne)
    # Anzahl Few-Shot-Beispiele = alle Paare außer system + aktueller Bewertung.
    fewshot_anzahl = (len(nachrichten) - 2) // 2
    antwort = _invoke_mit_retry(nachrichten)
    return {
        "entwurf": antwort.content.strip(),
        "freigabe_noetig": braucht_freigabe(review_text, sterne),
        "risikowoerter": gefundene_risikowoerter(review_text),
        "fewshot_verwendet": fewshot_anzahl,
    }
