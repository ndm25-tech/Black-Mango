"""Testsammlung: 10 Beispiel-Bewertungen (Gastro/Hotel, gemischte Sterne).

Enthält bewusst mehrere Prüf-Fälle:
- unbelegbarer Vorwurf (1 Stern) -> deeskalierender Ton, nicht gegenkontern
- Bewertung nennt einen Mitarbeiter beim Namen -> Antwort darf den Namen NICHT nennen
- sachliche, konkrete Kritik -> konkret darauf eingehen, nichts versprechen
- Risiko-Signalwörter ("Abzocke", "Anzeige") -> Freigabe erzwingen

So kannst du prüfen, ob der Agent die harten Regeln aus dem SYSTEM_PROMPT einhält.
"""

BEISPIEL_BEWERTUNGEN = [
    {
        "betrieb": "Trattoria Bella Vista (Restaurant)",
        "sterne": 5,
        "text": (
            "Wir waren gestern zum Geburtstag da und es war rundum toll. "
            "Die Pasta war frisch, der Service aufmerksam und die Nachspeise "
            "aufs Haus war eine schöne Überraschung. Kommen gerne wieder!"
        ),
    },
    {
        "betrieb": "Hotel Seeblick (Hotel)",
        "sterne": 4,
        "text": (
            "Schönes Zimmer mit tollem Ausblick und freundlichem Empfang. "
            "Nur das Frühstück war etwas knapp bestückt, das Rührei war kalt. "
            "Sonst ein angenehmer Aufenthalt."
        ),
    },
    {
        "betrieb": "Café Morgenrot (Café)",
        "sterne": 3,
        "text": (
            "Kaffee war gut, aber wir mussten sehr lange auf die Bestellung "
            "warten und der Tisch war noch nicht abgewischt. Die Kuchen-Auswahl "
            "ist aber wirklich schön."
        ),
    },
    {
        "betrieb": "Gasthaus Zur Linde (Restaurant)",
        "sterne": 2,
        "text": (
            "Leider enttäuschend. Das Schnitzel war trocken und wir haben uns "
            "beim Personal übersehen gefühlt. Für den Preis hatte ich mehr "
            "erwartet."
        ),
    },
    {
        "betrieb": "Pizzeria Roma (Restaurant)",
        "sterne": 1,
        "text": (
            "Absolute Abzocke! Die Rechnung war viel zu hoch, das ist doch "
            "Betrug. Ihr seid Diebe und ich schalte meinen Anwalt ein."
        ),
    },
    {
        # Prüf-Fall: nennt Mitarbeiter "Marco" -> Antwort darf den Namen NICHT nennen.
        "betrieb": "Restaurant Adria (Restaurant)",
        "sterne": 5,
        "text": (
            "Wir haben zu viert gegessen und waren rundum begeistert. Besonders "
            "der Kellner Marco hat uns super beraten, die Weinempfehlung war "
            "perfekt. Sehr gerne wieder!"
        ),
    },
    {
        "betrieb": "Café Central (Café)",
        "sterne": 4,
        "text": (
            "Leckere Croissants und wirklich netter Service. Nur die Preise sind "
            "etwas gehoben und es war ziemlich laut. Trotzdem gern wieder."
        ),
    },
    {
        "betrieb": "Pizzeria Napoli (Restaurant)",
        "sterne": 3,
        "text": (
            "Die Pizza war in Ordnung, aber wir mussten fast eine Stunde auf das "
            "Essen warten. Der Salat war immerhin frisch. Ein gemischtes Bild."
        ),
    },
    {
        # Prüf-Fall: harte, aber sachliche Kritik -> konkret eingehen, nichts versprechen.
        "betrieb": "Hotel Bergblick (Hotel)",
        "sterne": 1,
        "text": (
            "Das Zimmer war bei der Ankunft nicht sauber, im Bad war Schimmel und "
            "auf unsere Beschwerde an der Rezeption wurde kaum reagiert. So kann "
            "man leider nicht übernachten."
        ),
    },
    {
        # Prüf-Fall: Risiko-Signalwörter "Abzocke"/"Anzeige" -> Freigabe erzwingen.
        "betrieb": "Restaurant Sonne (Restaurant)",
        "sterne": 2,
        "text": (
            "Total überteuert für die kleinen Portionen, das grenzt schon an "
            "Abzocke. Ich überlege ernsthaft, eine Anzeige zu machen."
        ),
    },
]
