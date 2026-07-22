# Kudora 💬

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

# 3. Demo starten (nur Entwürfe ansehen)
python demo.py            # echte Entwürfe via Gemini
python demo.py --offline  # Trockenlauf ohne API-Key (nur Freigabe-Logik)

# 4. Freigabe + Gedächtnis (Woche 2): Entwurf prüfen und speichern
python freigabe.py            # echte Entwürfe, ENTER=übernehmen / Text=korrigieren
python freigabe.py --offline  # ohne API-Key testbar; schreibt daten/protokoll.csv

# 5. Oberfläche starten — am einfachsten mit dem Start-Skript:
bash start.sh                 # aktiviert .venv UND startet die App (ein Befehl)
# ... oder klassisch:
streamlit run app.py
```

> 💡 `bash start.sh` verhindert „command not found" (aktiviert automatisch die
> Umgebung). Und falls ein Modell abgeschaltet wurde, wechselt die App selbstständig
> auf ein aktuelles (siehe `FALLBACK_MODELLE` in `agent.py`).

## 👤 / 🛠️ Zwei Ansichten

- **Kunden-Ansicht (Standard):** Bewertung → fertige Antwort → „✅ Übernehmen".
  Keine Technik sichtbar, immer online. Jede übernommene Antwort lehrt den Agenten
  automatisch (Stil-Vorbild fürs nächste Mal).
- **Entwickler-Bereich (geheim):** komplett unsichtbar — kein Knopf, kein Passwortfeld.
  Zugang nur über die geheime URL `deine-app-url/?code=<ENTWICKLER_PASSWORT>`.
  Enthält: Training (Übungs-Bewertungen), Gedächtnis ansehen/löschen, Status.
  Ohne gesetztes Passwort ist der Bereich komplett deaktiviert.

## 📁 Struktur

```
Black-Mango/
├── requirements.txt
├── .env.example              # Vorlage für GOOGLE_API_KEY / MODEL_NAME / LERNPHASE
├── demo.py                   # führt alle Beispiel-Bewertungen durch (nur Anzeige)
├── freigabe.py               # Freigabe-Schritt (Kommandozeile): übernehmen/korrigieren
├── app.py                    # Streamlit-Oberfläche: Freigabe per Klick
├── daten/                    # Lern-Protokoll (protokoll.csv, gitignored)
└── bewertungsagent/
    ├── config.py             # Umgebungsvariablen, Modellname, Lernphase-Schalter
    ├── agent.py              # System-Prompt, Entwurf erzeugen, Freigabe-Logik
    ├── protokoll.py          # Gedächtnis: Protokoll speichern/laden (CSV)
    ├── stil_bibliothek.py    # menschliche Muster-Antworten als Grund-Vorbild
    └── beispiele.py          # Test-Bewertungen (Gastro/Hotel, gemischte Sterne)
```

## 🔒 Regeln (Recht & Sicherheit)

Der System-Prompt in `agent.py` erzwingt u. a.: Sie-Form, echte Umlaute, konkrete
Antworten statt Floskeln, nichts erfinden/versprechen, bei unbelegbaren Vorwürfen
nicht gegenkontern, keine Mitarbeiternamen, 2–4 Sätze. Zusätzlich erzwingt
`braucht_freigabe()` eine menschliche Prüfung – in der Lernphase immer, sonst bei
< 5 Sternen oder erkannten Risiko-Signalwörtern.

## 🌍 Veröffentlichen (Streamlit Community Cloud, kostenlos)

1. Auf **https://share.streamlit.io** gehen → mit **GitHub** anmelden.
2. **"Create app"** → Repository `ndm25-tech/Black-Mango`, Branch `main`,
   Main file path: `app.py` → **Deploy**.
3. In den App-Einstellungen unter **Secrets** eintragen (statt der lokalen `.env`):
   ```toml
   GOOGLE_API_KEY = "dein-key"
   ENTWICKLER_PASSWORT = "dein-geheimes-wort"
   ```
4. Fertig — die App bekommt eine feste URL (z. B. `https://….streamlit.app`) und
   läuft ohne deinen Rechner, auch vom Handy nutzbar.

> ⚠️ Ehrlicher Hinweis: In der Cloud ist `daten/protokoll.csv` **flüchtig** — bei
> jedem Neustart der App beginnt das Gedächtnis dort leer. Für Demos und erste
> Kunden okay; eine echte Datenbank kommt mit der Zapier-/Automatik-Stufe.

## 🗺️ Roadmap

- **Woche 1:** Projektstruktur, modularer Agent, Testsammlung, Demo. ✅
- **Woche 2:** Lern-Protokoll (Original + Entwurf + finale Antwort +
  „geändert?") in CSV speichern (`protokoll.py` + `freigabe.py`). ✅
- **Woche 3 (jetzt):** Few-Shot – die besten (unveränderten) gespeicherten
  Antworten werden automatisch als Vorbild in den Prompt geladen
  (`agent.baue_nachrichten`). Damit „lernt" der Agent deinen Stil. ✅
- **Woche 4 (jetzt):** Streamlit-Oberfläche (`app.py`) mit Freigabe-Button. ✅
- **Später:** Google-Anbindung (Zapier-Webhook), echter Testbetrieb, Ton feinjustieren.
