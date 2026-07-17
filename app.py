"""Bewertungs-Antwort-Agent — Produkt-Oberfläche.

Zwei Ansichten:
- KUNDEN-ANSICHT (Standard): radikal einfach. Bewertung -> fertige Antwort ->
  1 Klick übernehmen. Keine Technik sichtbar. Immer online (Gemini).
- ENTWICKLER-BEREICH (geheim, nur mit ENTWICKLER_PASSWORT aus der .env):
  Gedächtnis verwalten, eigene Bewertungen testen/lehren, Status.

Lernen passiert automatisch: JEDE übernommene Antwort (positiv wie negativ) wird
gespeichert und dient beim nächsten Entwurf als Stil-Vorbild.

Starten:  bash start.sh   (oder: streamlit run app.py)
"""

import streamlit as st

from bewertungsagent import agent, config, protokoll
from bewertungsagent.beispiele import BEISPIEL_BEWERTUNGEN

st.set_page_config(page_title="Bewertungs-Antwort-Agent", page_icon="💬")


# ------------------------------------------------------------------ Hilfsfunktionen
def erzeuge_antwort(betrieb: str, text: str, sterne: int):
    """Erzeugt eine Antwort via Gemini. Gibt (antwort, fehlermeldung) zurück."""
    try:
        with st.spinner("Antwort wird erstellt …"):
            ergebnis = agent.antwort_erzeugen(betrieb, text, sterne)
        return ergebnis["entwurf"], None
    except agent.TageslimitErreicht as fehler:
        return None, str(fehler)
    except Exception as fehler:  # noqa: BLE001 - dem Nutzer verständlich zeigen
        return None, f"Die Antwort konnte gerade nicht erstellt werden. ({fehler})"


# ------------------------------------------------------------------ Session-State
for schluessel, startwert in {
    "index": 0,          # Position in der Bewertungs-Warteschlange (Kunden-Ansicht)
    "entwurf": "",
    "entwurf_fuer": -1,  # für welchen Index der Entwurf gilt
    "fehler_fuer": -1,   # für welchen Index die Erzeugung fehlschlug (kein Endlos-Retry)
    "gen": 0,            # zählt Neu-Generierungen -> frisches Textfeld
    "dev": False,        # Entwickler-Bereich freigeschaltet?
}.items():
    if schluessel not in st.session_state:
        st.session_state[schluessel] = startwert


# ------------------------------------------------------------------ Seitenleiste
st.sidebar.title("💬 Bewertungs-Antwort")
st.sidebar.caption("Ihre Antwort auf jede Google-Bewertung — fertig zum Einfügen.")

# Geheimer Zugang: nur wenn ein Passwort konfiguriert ist, existiert das Feld überhaupt.
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
    tab_gedaechtnis, tab_eigene, tab_status = st.tabs(
        ["🧠 Gedächtnis", "✍️ Eigene Bewertung", "📊 Status"]
    )

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

    with tab_eigene:
        st.caption("Eigene Bewertung testen — die übernommene Antwort lehrt den Agenten.")
        with st.form("eigene_bewertung"):
            e_betrieb = st.text_input("Betrieb", value="Mein Betrieb")
            e_sterne = st.select_slider("Sterne", options=[1, 2, 3, 4, 5], value=5)
            e_text = st.text_area("Bewertungstext", height=120)
            absenden = st.form_submit_button("Antwort erzeugen")
        if absenden and e_text.strip():
            antwort, fehler = erzeuge_antwort(e_betrieb, e_text, e_sterne)
            if fehler:
                st.error(fehler)
            else:
                st.session_state.eigene_antwort = antwort
                st.session_state.eigene_daten = (e_betrieb, e_text, e_sterne)
        if st.session_state.get("eigene_antwort"):
            final = st.text_area(
                "Antwort (bearbeitbar):", value=st.session_state.eigene_antwort, height=150
            )
            if st.button("✅ Übernehmen & lernen"):
                b, t, s = st.session_state.eigene_daten
                protokoll.speichere(b, s, t, st.session_state.eigene_antwort, final)
                st.session_state.eigene_antwort = ""
                st.success("Gespeichert — der Agent lernt daraus.")

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
st.title("💬 Bewertungs-Antwort-Agent")
st.caption("Für jede Bewertung eine fertige, persönliche Antwort — sofort einsetzbar.")

gesamt = len(BEISPIEL_BEWERTUNGEN)
i = st.session_state.index

if i >= gesamt:
    st.success("🎉 Alle Bewertungen sind beantwortet!")
    if st.button("Von vorne beginnen"):
        st.session_state.index = 0
        st.session_state.entwurf_fuer = -1
        st.session_state.fehler_fuer = -1
        st.rerun()
    st.stop()

bewertung = BEISPIEL_BEWERTUNGEN[i]

st.caption(f"Bewertung {i + 1} von {gesamt}")
st.progress(i / gesamt)
st.subheader(bewertung["betrieb"])
st.write("⭐" * bewertung["sterne"] + f"  ({bewertung['sterne']}/5)")
st.info(bewertung["text"])

# Sanfter Hinweis bei heiklen Bewertungen — ohne technische Details.
if agent.gefundene_risikowoerter(bewertung["text"]):
    st.warning("Diese Bewertung ist heikel — bitte die Antwort besonders aufmerksam prüfen.")

# Antwort automatisch erzeugen (immer online via Gemini).
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

if not hat_entwurf:
    knopf1, knopf2 = st.columns(2)
    if knopf1.button("🔄 Erneut versuchen", type="primary"):
        st.session_state.fehler_fuer = -1
        st.rerun()
    if knopf2.button("⏭️ Nächste Bewertung"):
        st.session_state.index += 1
        st.session_state.entwurf_fuer = -1
        st.session_state.fehler_fuer = -1
        st.rerun()
    st.stop()

finale_antwort = st.text_area(
    "Ihre Antwort (bei Bedarf anpassen):",
    value=st.session_state.entwurf,
    height=170,
    key=f"textfeld_{i}_{st.session_state.gen}",
)

spalte1, spalte2, spalte3 = st.columns(3)
if spalte1.button("✅ Antwort übernehmen", type="primary"):
    protokoll.speichere(
        bewertung["betrieb"],
        bewertung["sterne"],
        bewertung["text"],
        st.session_state.entwurf,
        finale_antwort,
    )
    st.session_state.index += 1
    st.session_state.entwurf_fuer = -1
    st.session_state.fehler_fuer = -1
    st.rerun()

if spalte2.button("🔄 Andere Formulierung"):
    antwort, fehler = erzeuge_antwort(
        bewertung["betrieb"], bewertung["text"], bewertung["sterne"]
    )
    if fehler:
        st.error(fehler)
    else:
        st.session_state.entwurf = antwort
        st.session_state.gen += 1
        st.rerun()

if spalte3.button("⏭️ Nächste Bewertung"):
    st.session_state.index += 1
    st.session_state.entwurf_fuer = -1
    st.session_state.fehler_fuer = -1
    st.rerun()
