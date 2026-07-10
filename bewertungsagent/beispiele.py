"""Kleine Testsammlung: 5 Beispiel-Bewertungen (Gastro/Hotel, gemischte Sterne).

Enthält bewusst einen heiklen Fall (1 Stern mit unbelegbarem Vorwurf), damit
die Freigabe-Logik und der deeskalierende Ton geprüft werden können.
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
]
