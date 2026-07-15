"""Streamlit-Oberfläche für den Bewertungs-Antwort-Agenten (Woche 4).

Starten:
  streamlit run app.py

Zeigt jede Bewertung mit KI-Entwurf, lässt dich den Text anpassen und per Klick
freigeben. Freigegebene Antworten landen im Gedächtnis (protokoll.csv) und dienen
später als Few-Shot-Vorbild. Ohne API-Key im Offline-Modus bedienbar.
"""

import streamlit as st

from bewertungsagent import agent, config, protokoll
from bewertungsagent.beispiele import BEISPIEL_BEWERTUNGEN

st.set_page_config(page_title="Bewertungs-Antwort-Agent", page_icon="💬")


def hole_entwurf(bewertung: dict, offline: bool) -> str:
    """Liefert den Entwurf — echt via Gemini oder als Offline-Platzhalter."""
    if offline:
        return (
            f"[Offline-Platzhalter — hier stünde der Gemini-Entwurf "
            f"für {bewertung['betrieb']}]"
        )
    ergebnis = agent.antwort_erzeugen(
        bewertung["betrieb"], bewertung["text"], bewertung["sterne"]
    )
    return ergebnis["entwurf"]


def versuche_entwurf(bewertung: dict, offline: bool, index: int) -> bool:
    """Erzeugt einen Entwurf und fängt API-Limits sauber ab (kein Absturz)."""
    try:
        with st.spinner("Gemini schreibt …" if not offline else "…"):
            st.session_state.entwurf = hole_entwurf(bewertung, offline)
        st.session_state.entwurf_fuer = index
        return True
    except agent.TageslimitErreicht as fehler:
        st.error(f"🚦 {fehler}")
    except Exception as fehler:  # noqa: BLE001 - dem Nutzer klar anzeigen
        st.error(f"Gemini-Aufruf fehlgeschlagen: {fehler}")
    return False


# ---------------------------------------------------------------- Seitenleiste
st.sidebar.title("⚙️ Einstellungen")
offline = st.sidebar.checkbox(
    "Offline-Modus (ohne Gemini)", value=not bool(config.GOOGLE_API_KEY)
)
st.sidebar.write("API-Key gefunden:", "✅ ja" if config.GOOGLE_API_KEY else "❌ nein")
st.sidebar.write("Modell:", agent.aktives_modell())
st.sidebar.write("Protokoll-Einträge:", len(protokoll.lade_alle()))
st.sidebar.write(
    "Few-Shot-Vorbilder:", len(protokoll.beste_beispiele(n=config.ANZAHL_FEWSHOT))
)

# ---------------------------------------------------------------------- Zustand
if "index" not in st.session_state:
    st.session_state.index = 0
if "entwurf" not in st.session_state:
    st.session_state.entwurf = ""
if "entwurf_fuer" not in st.session_state:
    st.session_state.entwurf_fuer = -1

# ------------------------------------------------------------------- Hauptseite
st.title("💬 Bewertungs-Antwort-Agent")
st.caption(
    "Entwurf prüfen, bei Bedarf anpassen, freigeben. "
    "Freigegebene Antworten kommen ins Gedächtnis."
)

gesamt = len(BEISPIEL_BEWERTUNGEN)
i = st.session_state.index

if i >= gesamt:
    st.success(
        f"🎉 Alle {gesamt} Bewertungen bearbeitet! "
        f"Das Protokoll hat jetzt {len(protokoll.lade_alle())} Einträge."
    )
    if st.button("Von vorne beginnen"):
        st.session_state.index = 0
        st.session_state.entwurf_fuer = -1
        st.rerun()
    st.stop()

bewertung = BEISPIEL_BEWERTUNGEN[i]

st.caption(f"Bewertung {i + 1} von {gesamt}")
st.progress(i / gesamt)

st.subheader(bewertung["betrieb"])
st.write("⭐" * bewertung["sterne"] + f"  ({bewertung['sterne']}/5)")
st.info(bewertung["text"])

# Warnungen (funktionieren auch offline, brauchen kein Gemini)
freigabe = agent.braucht_freigabe(bewertung["text"], bewertung["sterne"])
risiko = agent.gefundene_risikowoerter(bewertung["text"])
if risiko:
    st.error(
        f"⚠️ Risiko-Signalwörter erkannt: {', '.join(risiko)} "
        "— besonders sorgfältig prüfen, nicht gegenkontern."
    )
elif freigabe:
    st.warning("🔒 Freigabe nötig (Lernphase oder weniger als 5 Sterne).")

hat_entwurf = st.session_state.entwurf_fuer == i

# Offline ist gratis -> Entwurf sofort erzeugen. Echt-Modus -> erst auf Klick (spart Anfragen).
if offline and not hat_entwurf:
    versuche_entwurf(bewertung, offline=True, index=i)
    hat_entwurf = st.session_state.entwurf_fuer == i

if not hat_entwurf:
    st.caption("Noch kein Entwurf — jede Erzeugung verbraucht eine Gemini-Anfrage.")
    knopf1, knopf2 = st.columns(2)
    if knopf1.button("✍️ Entwurf mit Gemini erzeugen", type="primary"):
        if versuche_entwurf(bewertung, offline=False, index=i):
            st.rerun()
    if knopf2.button("⏭️ Überspringen"):
        st.session_state.index += 1
        st.session_state.entwurf_fuer = -1
        st.rerun()
    st.stop()

finale_antwort = st.text_area(
    "KI-Entwurf (bearbeitbar):",
    value=st.session_state.entwurf,
    height=170,
    key=f"textfeld_{i}",
)

spalte1, spalte2, spalte3 = st.columns(3)
if spalte1.button("✅ Freigeben & speichern", type="primary"):
    protokoll.speichere(
        bewertung["betrieb"],
        bewertung["sterne"],
        bewertung["text"],
        st.session_state.entwurf,  # der Original-Entwurf
        finale_antwort,            # ggf. von dir angepasst
    )
    st.session_state.index += 1
    st.session_state.entwurf_fuer = -1
    st.rerun()

if spalte2.button("🔄 Neu generieren"):
    if versuche_entwurf(bewertung, offline, index=i):
        st.rerun()

if spalte3.button("⏭️ Überspringen"):
    st.session_state.index += 1
    st.session_state.entwurf_fuer = -1
    st.rerun()
