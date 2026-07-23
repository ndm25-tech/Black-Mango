# Kudora online stellen (Server + Erweiterung für echte Kunden)

Ziel: Der Server läuft dauerhaft im Netz, die Erweiterung nutzt ihn automatisch,
und du kannst sie einem echten Café/Restaurant per Link geben — **ohne**
Entwicklermodus.

Reihenfolge: **A) Server (Render)** → **B) Erweiterung einstellen** →
**C) Chrome Web Store**.

---

## A) Server auf Render hosten (~5–7 €/Monat, immer an)

1. Auf **https://render.com** mit **GitHub** anmelden.
2. **„New +" → „Blueprint"** → Repository **`ndm25-tech/Black-Mango`** wählen →
   Render liest die `render.yaml` automatisch → **Apply**.
   *(Alternativ: „New +" → „Web Service" → Repo wählen → Start Command
   `uvicorn api:app --host 0.0.0.0 --port $PORT`, Plan „Starter".)*
3. Unter **Environment / Secrets** zwei Werte eintragen:
   - `GOOGLE_API_KEY` = dein Google-Gemini-Key (derselbe wie lokal)
   - `KUDORA_TOKEN` = dein Geheim-Token, z. B.
     `kdr_F3gvG46ONpGfOh4fYB6O-flHM0wSWv5c` *(oder ein eigenes)*
4. **Deploy** abwarten. Render gibt dir eine feste Adresse, z. B.
   `https://kudora-api.onrender.com`.
5. **Test:** Diese Adresse im Browser öffnen → es muss
   `{"status":"ok","modell":"…"}` erscheinen.

> Hinweis: Das Gedächtnis (`daten/protokoll.csv`) liegt auf dem Server und kann
> bei einem Neu-Deploy zurückgesetzt werden. Für den Pilottest okay; eine echte
> Datenbank kommt später.

---

## B) Erweiterung auf den Server zeigen lassen

Datei **`extension/config.js`** öffnen und **zwei Werte** eintragen:

```js
self.KUDORA_CONFIG = {
  backendUrl: "https://kudora-api.onrender.com", // deine Render-Adresse, ohne / am Ende
  token: "kdr_F3gvG46ONpGfOh4fYB6O-flHM0wSWv5c", // GLEICHES Token wie KUDORA_TOKEN
};
```

Danach `chrome://extensions` → Kudora **↻**. (Für dich selbst zum Testen kannst du
hier auch wieder `http://localhost:8000` + leeres Token eintragen.)

---

## C) In den Chrome Web Store (unlisted = nur mit Link)

1. Den Ordner **`extension/`** als **ZIP** verpacken.
2. **https://chrome.google.com/webstore/devconsole** öffnen → einmalig **5 $**
   Entwicklergebühr zahlen.
3. **„New item"** → ZIP hochladen.
4. Store-Eintrag ausfüllen: Name „Kudora", kurze Beschreibung, Icon, mindestens
   ein Screenshot, und die **Datenschutzerklärung** (siehe
   [`datenschutz.md`](datenschutz.md) — Text online stellen und die URL eintragen).
5. **Sichtbarkeit: „Unlisted"** → **Veröffentlichen**. Nach der Prüfung (meist
   ein paar Tage) bekommst du einen **Installations-Link**.
6. Diesen Link deinem Pilot-Café geben → ein Klick, fertig, kein Entwicklermodus.

---

## Kurz-Check vor dem ersten Kunden
- [ ] Render-Adresse im Browser zeigt `{"status":"ok"}`.
- [ ] `config.js` hat die Render-Adresse **und** das gleiche Token wie Render.
- [ ] Bei dir getestet: Bewertung → „✨ Mit Kudora antworten" → Antwort → Senden.
- [ ] Store-Eintrag „Unlisted", Datenschutz-Link gesetzt.
