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

st.set_page_config(page_title="Bewertungs-Antwort", page_icon="💬")

# Feinschliff fürs dunkle Theme (.streamlit/config.toml): runde Knöpfe, weiche Karten.
st.markdown(
    """
    <style>
      .stButton > button {
          border-radius: 10px;
          padding: 0.55rem 1.1rem;
          font-weight: 600;
          border: 1px solid rgba(232, 163, 61, 0.35);
      }
      .stButton > button:hover { border-color: #e8a33d; }
      .stTextArea textarea, .stTextInput input { border-radius: 10px; }
      div[data-testid="stAlert"] { border-radius: 12px; }
      .stProgress > div > div > div { background-color: #e8a33d; }
      h3 { letter-spacing: 0.2px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ Hilfsfunktionen
def erzeuge_antwort(betrieb: str, text: str, sterne: int):
    """Erzeugt eine Antwort via Gemini. Gibt (antwort, fehlermeldung) zurück."""
    try:
        with st.spinner("Ihre Antwort wird erstellt …"):
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
st.sidebar.title("💬 Bewertungs-Antwort")
st.sidebar.caption("Ihre Antwort auf jede Google-Bewertung — fertig zum Einfügen.")

if config.ENTWICKLER_PASSWORT:
    with st.sidebar.expander("🔧", expanded=False):
        eingabe = st.text_input("Zugangscode", type="password", key="dev_pw")
        if eingabe and eingabe == config.ENTWICKLER_PASSWORT:
            st.session_state.dev = True
        elif eingabe:
            st.caption("Falscher Code.")

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
                if s1.button("✅ Freigeben", type="primary", key="tr_ok"):
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
                if s3.button("⏭️ Weiter", key="tr_skip"):
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
    if k1.button("✅ Antwort übernehmen", type="primary"):
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
    if k3.button("↩️ Neue Bewertung"):
        st.session_state.kunde_antwort = ""
        st.session_state.kunde_daten = None
        st.rerun()
