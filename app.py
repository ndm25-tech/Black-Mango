"""Bewertungs-Antwort-Agent — Produkt-Oberfläche.

Zwei Ansichten:
- KUNDEN-ANSICHT (Standard): eigene Google-Bewertung einfügen -> fertige,
  persönliche Antwort -> übernehmen. Keine Technik, keine Testdaten sichtbar.
- ENTWICKLER-BEREICH (geheim, nur mit ENTWICKLER_PASSWORT):
  Training (Übungs-Bewertungen), Gedächtnis verwalten, Status.

Lernen passiert automatisch: JEDE übernommene Antwort (positiv wie negativ) wird
gespeichert und dient beim nächsten Entwurf als Stil-Vorbild.

Starten:  bash start.sh   (oder: streamlit run app.py)
"""

import streamlit as st

from bewertungsagent import agent, config, protokoll
from bewertungsagent.beispiele import BEISPIEL_BEWERTUNGEN

st.set_page_config(page_title="Kudora", page_icon="💬")

# Premium-SaaS-Styling (nur Optik): Typografie, Karten, Buttons, Animationen.
st.markdown(
    """
    <style>
      /* ---------- Typografie ---------- */
      html, body, [class*="css"] { line-height: 1.6; }
      h1 { font-size: 2.1rem !important; font-weight: 700; letter-spacing: -0.02em; }
      h2 { font-size: 1.5rem !important; font-weight: 650; }
      h3 { font-size: 1.2rem !important; letter-spacing: 0.2px; }
      p, label, .stMarkdown { font-size: 1.0rem; }

      /* ---------- Seite: sanftes Einblenden, mehr Luft ---------- */
      @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
      }
      section.main .block-container {
          animation: fadeInUp 0.35s ease-out;
          padding-top: 2.5rem;
          padding-bottom: 3rem;
          max-width: 46rem;
      }

      /* ---------- Header (zentriert) ---------- */
      .app-header {
          display: flex; flex-direction: column; align-items: center;
          padding: 1.6rem 0 0.2rem 0;
      }
      .app-logo {
          width: 46px; height: 46px; border-radius: 12px;
          background: linear-gradient(135deg, #6366F1, #8B5CF6);
          display: flex; align-items: center; justify-content: center;
          font-size: 22px; box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35);
      }
      .app-title { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em;
                   color: #E6E9F2; margin: 10px 0 0 0; text-align: center; }
      .app-subtitle {
          text-align: center;
          font-size: 15px;
          font-weight: 450;
          color: #9CA3AF;
          margin: 7px 0 20px 0;
      }

      /* ---------- Karten / Formulare ---------- */
      div[data-testid="stForm"] {
          background: #161C2D;
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 14px;
          padding: 1.6rem 1.6rem 1.2rem 1.6rem;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      }
      div[data-testid="stAlert"] {
          border-radius: 12px;
          padding: 0.9rem 1.1rem;
          border: 1px solid rgba(255, 255, 255, 0.05);
      }
      div[data-testid="stVerticalBlock"] > div { margin-bottom: 0.25rem; }

      /* ---------- Eingaben ---------- */
      .stTextArea textarea, .stTextInput input {
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.08) !important;
          font-size: 1.0rem; line-height: 1.6;
      }
      .stTextArea textarea:focus, .stTextInput input:focus {
          border-color: #6366F1 !important;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
      }

      /* ---------- Buttons ---------- */
      .stButton > button, .stFormSubmitButton > button {
          border-radius: 11px;
          padding: 0.6rem 1.2rem;
          font-weight: 600;
          border: 1px solid rgba(99, 102, 241, 0.35);
          transition: transform 0.15s ease, border-color 0.15s ease,
                      box-shadow 0.15s ease;
      }
      .stButton > button:hover, .stFormSubmitButton > button:hover {
          transform: scale(1.02);
          border-color: #6366F1;
          box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25);
      }
      .stButton > button:active { transform: scale(0.99); }

      /* ---------- Progressbar ---------- */
      .stProgress > div > div {
          height: 10px !important; border-radius: 999px;
      }
      .stProgress > div > div > div {
          height: 10px !important; border-radius: 999px;
          background: linear-gradient(90deg, #6366F1, #8B5CF6) !important;
      }

      /* ---------- Lade-Animation (Spinner-Puls) ---------- */
      @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.55; } }
      div[data-testid="stSpinner"] > div {
          animation: pulse 1.4s ease-in-out infinite;
          font-size: 1.02rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ Hilfsfunktionen
def erzeuge_antwort(betrieb: str, text: str, sterne: int):
    """Erzeugt eine Antwort via Gemini. Gibt (antwort, fehlermeldung) zurück."""
    try:
        with st.spinner("✨ KI erstellt gerade eine natürliche Antwort..."):
            ergebnis = agent.antwort_erzeugen(betrieb, text, sterne)
        return ergebnis["entwurf"], None
    except agent.TageslimitErreicht as fehler:
        return None, str(fehler)
    except Exception as fehler:  # noqa: BLE001 - dem Nutzer verständlich zeigen
        return None, f"Die Antwort konnte gerade nicht erstellt werden. ({fehler})"


# ------------------------------------------------------------------ Session-State
for schluessel, startwert in {
    # Kunden-Ansicht (eigene Bewertung)
    "kunde_antwort": "",
    "kunde_daten": None,      # (betrieb, text, sterne) der aktuellen Bewertung
    "kunde_gen": 0,           # frisches Textfeld nach "Andere Formulierung"
    "kunde_fertig": False,    # gerade übernommen -> Erfolgsmeldung zeigen
    # Training (Entwickler)
    "index": 0,
    "entwurf": "",
    "entwurf_fuer": -1,
    "fehler_fuer": -1,
    "gen": 0,
    # Entwickler-Zugang
    "dev": False,
}.items():
    if schluessel not in st.session_state:
        st.session_state[schluessel] = startwert


# ------------------------------------------------------------------ Seitenleiste
st.sidebar.title("💬 Kudora")
st.sidebar.caption("Ihre Antwort auf jede Google-Bewertung — fertig zum Einfügen.")

# Entwickler-Zugang: KEIN sichtbarer Knopf, kein Passwortfeld. Der Bereich öffnet
# sich nur über die geheime URL  …/?code=<ENTWICKLER_PASSWORT>  — Besucher der
# normalen Adresse sehen ausschließlich die Kunden-Ansicht.
if config.ENTWICKLER_PASSWORT:
    if st.query_params.get("code") == config.ENTWICKLER_PASSWORT:
        st.session_state.dev = True

ansicht = "Kunde"
if st.session_state.dev:
    ansicht = st.sidebar.radio("Ansicht", ["Kunde", "Entwickler"], index=1)


# ================================================================== ENTWICKLER
if ansicht == "Entwickler":
    st.title("🛠️ Entwickler-Bereich")
    tab_training, tab_gedaechtnis, tab_status = st.tabs(
        ["🎓 Training", "🧠 Gedächtnis", "📊 Status"]
    )

    # ---- Training: die Übungs-Bewertungen durcharbeiten (lehrt den Agenten) ----
    with tab_training:
        gesamt = len(BEISPIEL_BEWERTUNGEN)
        i = st.session_state.index

        if i >= gesamt:
            st.success("🎉 Alle Übungs-Bewertungen bearbeitet!")
            if st.button("Von vorne beginnen"):
                st.session_state.index = 0
                st.session_state.entwurf_fuer = -1
                st.session_state.fehler_fuer = -1
                st.rerun()
        else:
            bewertung = BEISPIEL_BEWERTUNGEN[i]
            st.caption(f"Übungs-Bewertung {i + 1} von {gesamt}")
            st.progress(i / gesamt)
            st.subheader(bewertung["betrieb"])
            st.write("⭐" * bewertung["sterne"] + f"  ({bewertung['sterne']}/5)")
            st.info(bewertung["text"])
            if agent.gefundene_risikowoerter(bewertung["text"]):
                st.warning("Heikle Bewertung — Antwort besonders aufmerksam prüfen.")

            hat_entwurf = st.session_state.entwurf_fuer == i
            if not hat_entwurf and st.session_state.fehler_fuer != i:
                antwort, fehler = erzeuge_antwort(
                    bewertung["betrieb"], bewertung["text"], bewertung["sterne"]
                )
                if fehler:
                    st.session_state.fehler_fuer = i
                    st.error(fehler)
                else:
                    st.session_state.entwurf = antwort
                    st.session_state.entwurf_fuer = i
                    hat_entwurf = True

            if hat_entwurf:
                finale = st.text_area(
                    "Antwort (bearbeitbar):",
                    value=st.session_state.entwurf,
                    height=160,
                    key=f"training_{i}_{st.session_state.gen}",
                )
                s1, s2, s3 = st.columns(3)
                if s1.button("✔ Freigeben", type="primary", key="tr_ok"):
                    protokoll.speichere(
                        bewertung["betrieb"], bewertung["sterne"], bewertung["text"],
                        st.session_state.entwurf, finale,
                    )
                    st.session_state.index += 1
                    st.session_state.entwurf_fuer = -1
                    st.session_state.fehler_fuer = -1
                    st.rerun()
                if s2.button("🔄 Neu", key="tr_neu"):
                    antwort, fehler = erzeuge_antwort(
                        bewertung["betrieb"], bewertung["text"], bewertung["sterne"]
                    )
                    if fehler:
                        st.error(fehler)
                    else:
                        st.session_state.entwurf = antwort
                        st.session_state.gen += 1
                        st.rerun()
                if s3.button("➜ Weiter", key="tr_skip"):
                    st.session_state.index += 1
                    st.session_state.entwurf_fuer = -1
                    st.session_state.fehler_fuer = -1
                    st.rerun()
            elif st.session_state.fehler_fuer == i:
                if st.button("🔄 Erneut versuchen", key="tr_retry"):
                    st.session_state.fehler_fuer = -1
                    st.rerun()

    # ---- Gedächtnis: Stil-Vorbilder ansehen und pflegen ----
    with tab_gedaechtnis:
        eintraege = protokoll.lade_alle()
        st.write(f"**{len(eintraege)} gespeicherte Antworten** (Stil-Vorbilder).")
        if eintraege:
            st.dataframe(
                [
                    {
                        "Nr": i,
                        "Betrieb": z.get("betrieb", ""),
                        "Sterne": z.get("sterne", ""),
                        "Antwort": (z.get("finale_antwort") or "")[:80],
                        "geändert": z.get("geaendert", ""),
                    }
                    for i, z in enumerate(eintraege)
                ],
                use_container_width=True,
                hide_index=True,
            )
            nummer = st.number_input(
                "Eintrag-Nr. löschen (schlechtes Vorbild entfernen):",
                min_value=0, max_value=len(eintraege) - 1, step=1,
            )
            if st.button("🗑️ Diesen Eintrag löschen"):
                if protokoll.loesche(int(nummer)):
                    st.success(f"Eintrag {int(nummer)} gelöscht.")
                    st.rerun()
        else:
            st.info("Noch keine Einträge — übernommene Antworten landen hier.")

    with tab_status:
        st.write("Modell:", agent.aktives_modell())
        st.write("API-Key gefunden:", "✅ ja" if config.GOOGLE_API_KEY else "❌ nein")
        st.write("Protokoll-Einträge:", len(protokoll.lade_alle()))
        st.write(
            "Few-Shot-Vorbilder:",
            len(protokoll.beste_beispiele(n=config.ANZAHL_FEWSHOT)),
        )
        st.write("Kreativität (Temperature):", config.TEMPERATURE)
    st.stop()


# ================================================================== KUNDE
# Schlicht: eigene Bewertung einfügen -> fertige Antwort. Keine Testdaten, keine Technik.
st.markdown(
    """
    <div class="app-header">
      <div class="app-logo">💬</div>
      <p class="app-title">Kudora</p>
    </div>
    <p class="app-subtitle">Professional AI Review Assistant</p>
    """,
    unsafe_allow_html=True,
)

if st.session_state.kunde_fertig:
    st.success("✅ Antwort übernommen — einfach bei Google einfügen. Die nächste Bewertung kann kommen!")
    st.session_state.kunde_fertig = False

if not st.session_state.kunde_antwort:
    with st.form("kunde_form"):
        text = st.text_area(
            "Google-Bewertung hier einfügen:",
            height=140,
            placeholder="z. B. „Das Essen war fantastisch, nur die Wartezeit war lang …“",
        )
        sterne = st.select_slider("Sterne der Bewertung", options=[1, 2, 3, 4, 5], value=5)
        betrieb = st.text_input("Name Ihres Betriebs (optional)", value="")
        absenden = st.form_submit_button("✨ Antwort erstellen", type="primary")

    if absenden:
        if not text.strip():
            st.warning("Bitte zuerst den Text der Bewertung einfügen.")
        else:
            antwort, fehler = erzeuge_antwort(betrieb.strip() or "unser Haus", text, sterne)
            if fehler:
                st.error(fehler)
            else:
                st.session_state.kunde_antwort = antwort
                st.session_state.kunde_daten = (betrieb.strip() or "unser Haus", text, sterne)
                st.rerun()
else:
    betrieb, text, sterne = st.session_state.kunde_daten
    st.write("⭐" * sterne + f"  ({sterne}/5)")
    st.info(text)
    if agent.gefundene_risikowoerter(text):
        st.warning("Diese Bewertung ist heikel — bitte die Antwort besonders aufmerksam prüfen.")

    finale_antwort = st.text_area(
        "Ihre Antwort (bei Bedarf anpassen):",
        value=st.session_state.kunde_antwort,
        height=170,
        key=f"kunde_feld_{st.session_state.kunde_gen}",
    )

    k1, k2, k3 = st.columns(3)
    if k1.button("✔ Antwort übernehmen", type="primary"):
        protokoll.speichere(betrieb, sterne, text, st.session_state.kunde_antwort, finale_antwort)
        st.session_state.kunde_antwort = ""
        st.session_state.kunde_daten = None
        st.session_state.kunde_fertig = True
        st.rerun()
    if k2.button("🔄 Andere Formulierung"):
        antwort, fehler = erzeuge_antwort(betrieb, text, sterne)
        if fehler:
            st.error(fehler)
        else:
            st.session_state.kunde_antwort = antwort
            st.session_state.kunde_gen += 1
            st.rerun()
    if k3.button("➜ Neue Bewertung"):
        st.session_state.kunde_antwort = ""
        st.session_state.kunde_daten = None
        st.rerun()
