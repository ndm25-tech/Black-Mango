# Google-Business-Profile-API — Freigabe beantragen (Vorbereitung)

> **Zweck:** Damit Kudora später Antworten **direkt** auf Google Maps posten kann
> (Stufe 2, ohne Chrome-Erweiterung), braucht es Zugang zur **Google-Business-
> Profile-API**. Diesen Zugang gibt Google nur nach einem **Antrag mit Prüfung**
> frei. Diese Datei bereitet alles vor — **einreichen musst du selbst** (es braucht
> dein Google-Konto). Für den **sofortigen** Live-Test nutzen wir die Chrome-
> Erweiterung; dieser Antrag läuft **parallel**.

## Ehrliche Einordnung (bitte zuerst lesen)
- Der Zugang ist **nicht automatisch** — Google **prüft** den Antrag. Ausgang und
  Dauer entscheidet Google (erfahrungsgemäß **Tage bis Wochen**, keine Garantie).
- Für **fremde** Betriebe (nicht nur dein eigenes Profil) kommt zusätzlich die
  **OAuth-App-Verifizierung** dazu (sensibler Scope) — nochmal eine Google-Prüfung.
- Es braucht später einen **dauerhaft laufenden Server + Datenbank** (für die
  Zugangs-Tokens der Kunden). Die kostenlose Streamlit-Cloud reicht dafür **nicht**.
- **Wichtig (Google-Regel):** Über die API **keine** Fake- oder gekauften Bewertungen
  erzeugen — das führt zur Sperrung. Kudora hilft nur beim **Antworten**, der Mensch
  gibt jede Antwort frei.

## Voraussetzungen (vor dem Antrag erfüllen)
1. **Google-Cloud-Projekt** (kostenlos): https://console.cloud.google.com
2. **Verifiziertes, aktives Google-Business-Profil** — üblich ist ein **mindestens
   ~60 Tage altes**, gepflegtes Profil.
3. **Gültige Website-URL** des Betriebs/Produkts (z. B. deine Kudora-Landingpage).
4. **Klare Beschreibung des Anwendungsfalls** (Text unten ist fertig zum Einfügen).
5. **Datenschutzerklärung** (öffentlich erreichbar) — wird für den OAuth-Consent
   verlangt.

## Schritt für Schritt
1. **Cloud-Projekt anlegen** → Projektname z. B. `kudora`, die **Projektnummer**
   notieren (brauchst du im Antrag).
2. **APIs aktivieren** in „APIs & Dienste → Bibliothek“ — die Business-Profile-APIs,
   u. a.:
   - *Google My Business API* (Reviews/Antworten, v4-Ressourcen)
   - *My Business Account Management API*
   - *My Business Business Information API*
3. **OAuth-Consent-Screen** einrichten (Nutzertyp **Extern**):
   - App-Name „Kudora“, Support-E-Mail, Logo, Links zu **Startseite** +
     **Datenschutzerklärung**.
   - **Scope** hinzufügen: `https://www.googleapis.com/auth/business.manage`.
   - Zum Testen dich selbst als **Test-Nutzer** eintragen.
4. **OAuth-Client-ID** erstellen (Typ „Webanwendung“) → Client-ID + Secret sicher
   speichern (kommen später auf den Server, **nie** in die Erweiterung/ins Repo).
5. **Zugangs-Antrag einreichen:** Googles **Business-Profile-API-Zugangsformular**
   ausfüllen (erreichbar über die offizielle Doku, siehe Links). Dort angeben:
   **Projektnummer**, **Kontakt-E-Mail**, **Website**, **Anwendungsfall** (Text unten).
6. **Auf Freigabe warten.** Danach ggf. **OAuth-Verifizierung** durchlaufen
   (Domain bestätigen, Datenschutzerklärung, evtl. Sicherheits-Check).

## Fertiger Begründungstext (zum Einfügen ins Antragsformular)
> **Application name:** Kudora
>
> **Use case:** Kudora is an assistant that helps small local businesses
> (restaurants, cafés, hotels) write professional, personal replies to their own
> Google reviews in German. For each review, Kudora drafts a suggested reply; the
> business owner reviews, edits if needed, and explicitly approves it before it is
> published. Kudora only creates **replies to existing reviews** — it never creates,
> solicits, or incentivizes reviews, and never posts without human approval. We
> request read access to the owner's reviews and permission to publish the owner's
> approved reply (`accounts.locations.reviews`, `updateReply`) via the
> `business.manage` scope. Data is processed only to draft the reply, handled per
> GDPR, and access is limited to businesses that connect their own account via OAuth.

*(Bei Bedarf ins Deutsche übersetzen — viele Google-Formulare erwarten Englisch.)*

## Was Kudora technisch nutzt (zur Info)
- **Reviews lesen / beantworten:** v4-Ressource `accounts.locations.reviews`
  (u. a. `list`, `updateReply`, `deleteReply`).
- **Scope:** `business.manage`.
- **Server-Aufgaben (Stufe 2):** OAuth-Tokens je Kunde speichern + auffrischen,
  Reviews abrufen, Kudora-Entwurf erzeugen (bestehende Logik in `bewertungsagent/`),
  freigegebene Antwort per `updateReply` posten.

## Offizielle Quellen (bitte final dort gegenprüfen)
- Google Business Profile APIs – Übersicht & Doku:
  https://developers.google.com/my-business
- Mit Review-Daten arbeiten (`accounts.locations.reviews`):
  https://developers.google.com/my-business/content/review-data
- Neueste Änderungen/Policies:
  https://developers.google.com/my-business/content/latest-updates

> Hinweis: Google ändert Formular und Ablauf gelegentlich. Die Schritte hier sind der
> Stand der Recherche (Juli 2026); **maßgeblich ist immer die offizielle Doku oben.**
