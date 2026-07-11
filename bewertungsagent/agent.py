"""Kern des Agenten: Antwort-Entwurf erzeugen + Freigabe-Logik.

- SYSTEM_PROMPT bündelt die harten Rechts-/Sicherheitsregeln.
- braucht_freigabe() entscheidet, ob ein Mensch drüberschauen muss.
  In der Lernphase (config.LERNPHASE) ist das IMMER True.

Der LLM-Import passiert bewusst erst beim ersten echten Aufruf (lazy),
damit sich das Modul ohne installiertes langchain importieren lässt.
"""

from . import config, protokoll

SYSTEM_PROMPT = """
Du schreibst für einen Gastronomie- oder Hotelbetrieb in Deutschland Antworten
auf Google-Bewertungen. Persönlich, warm und professionell, als käme die Antwort
vom Inhaber bzw. dem Team.

FESTE REGELN (immer einhalten):
- Antworte konkret auf den Inhalt der Bewertung, keine Standard-Floskeln.
- Immer Sie-Form. Echte Umlaute (ä, ö, ü, ß). Keine Ausrufezeichen-Flut.
- Bei Kritik: ruhig, sachlich, deeskalierend. Höchstens einmal "das tut uns leid".
- Nichts erfinden. Nichts versprechen (keine Gutscheine, Rabatte oder Zusagen).
- Bei unbelegbaren Vorwürfen (z. B. "ihr seid Diebe") NICHT mit einer
  Gegenbehauptung kontern ("Sie waren nie hier", "das ist gelogen"). Stattdessen
  ruhig bleiben, sachlich Bedauern/Überraschung ausdrücken und um direkten
  Kontakt zur Klärung bitten.
- Keine Mitarbeiternamen nennen, auch wenn die Bewertung sie nennt.
- Keine Werbung in der Antwort.
- Länge 2 bis 4 Sätze, mit einer freundlichen Grußformel im Namen des Teams.
- DSGVO: personenbezogene Daten sparsam behandeln.

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
        _llm = init_chat_model(config.MODEL_NAME, model_provider="google_genai")
    return _llm


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

    # Gedächtnis: die besten bisherigen Antworten als Vorbild (Bewertung -> Antwort).
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
    antwort = _get_llm().invoke(nachrichten)
    return {
        "entwurf": antwort.content.strip(),
        "freigabe_noetig": braucht_freigabe(review_text, sterne),
        "risikowoerter": gefundene_risikowoerter(review_text),
        "fewshot_verwendet": fewshot_anzahl,
    }
