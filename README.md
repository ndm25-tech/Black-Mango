# Bewertungs-Antwort-Agent 💬

Ein KI-Agent, der auf Google-Bewertungen von Betrieben passende, **deutsche**
Antworten entwirft. In der Lernphase geht **jede** Antwort zuerst zur
menschlichen Freigabe, bevor sie online geht.

**Muster:** Input (Bewertung) → LLM-Schritt (Entwurf) → Freigabe-Logik → Output.
**Zielmarkt:** zuerst Gastronomie & Hotels, später Arzt-/Zahnarztpraxen.

## 🛠️ Stack

| Technologie | Zweck |
|-------------|-------|
| Python | Sprache |
| LangChain | LLM-Anbindung (`init_chat_model`) |
| Google Gemini | Modell (`gemini-2.5-flash`) |
| python-dotenv | Laden des API-Keys aus `.env` |

## 🚀 Setup

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. API-Key hinterlegen
cp .env.example .env
#    -> GOOGLE_API_KEY in .env eintragen

# 3. Demo starten
python demo.py            # echte Entwürfe via Gemini
python demo.py --offline  # Trockenlauf ohne API-Key (nur Freigabe-Logik)
```

## 📁 Struktur

```
Black-Mango/
├── requirements.txt
├── .env.example              # Vorlage für GOOGLE_API_KEY / MODEL_NAME / LERNPHASE
├── demo.py                   # führt alle Beispiel-Bewertungen durch
└── bewertungsagent/
    ├── config.py             # Umgebungsvariablen, Modellname, Lernphase-Schalter
    ├── agent.py              # System-Prompt, Entwurf erzeugen, Freigabe-Logik
    └── beispiele.py          # 5 Test-Bewertungen (Gastro/Hotel, gemischte Sterne)
```

## 🔒 Regeln (Recht & Sicherheit)

Der System-Prompt in `agent.py` erzwingt u. a.: Sie-Form, echte Umlaute, konkrete
Antworten statt Floskeln, nichts erfinden/versprechen, bei unbelegbaren Vorwürfen
nicht gegenkontern, keine Mitarbeiternamen, 2–4 Sätze. Zusätzlich erzwingt
`braucht_freigabe()` eine menschliche Prüfung – in der Lernphase immer, sonst bei
< 5 Sternen oder erkannten Risiko-Signalwörtern.

## 🗺️ Roadmap

- **Woche 1 (jetzt):** Projektstruktur, modularer Agent, Testsammlung, Demo. ✅
- **Woche 2:** Lern-Protokoll (Original + Entwurf + finale Antwort + „geändert?")
  in CSV/SQLite speichern; Vorbereitung Google-Anbindung via Zapier-Webhook.
- **Woche 3:** Few-Shot – beste gespeicherte Antworten automatisch in den Prompt
  laden; einfache Streamlit-Oberfläche mit Freigabe-Button.
- **Woche 4:** Mit echtem Testbetrieb nutzen, Ton feinjustieren, stabilisieren.
