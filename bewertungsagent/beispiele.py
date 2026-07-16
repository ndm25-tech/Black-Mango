"""Testsammlung: 14 Beispiel-Bewertungen (Restaurants/Cafés in Bad Nauheim).

Ziel: möglichst UNTERSCHIEDLICHE Bewertungen über ALLE Sterne-Stufen (viele
5 Sterne, aber auch 4/3/2/1), damit man sieht, dass der Agent JEDE Bewertung
beantwortet — nicht nur die kritischen.

Wichtig: Das sind SYNTHETISCHE Test-Bewertungen. Es wurden echte Bad-Nauheimer
Lokal-Namen als Kontext verwendet, aber KEINE echten Kundenbewertungen kopiert
(Datenschutz/DSGVO).

Eingebaute Prüf-Fälle (halten die harten Regeln aus dem SYSTEM_PROMPT?):
- nennt Mitarbeiter beim Namen (Deutsches Haus)  -> Name darf NICHT auftauchen
- sachliche, ernste Beschwerde (Tajine 1*)       -> konkret, ruhig, nichts versprechen
- Risiko-Signalwörter "Abzocke"/"Anzeige" (Da Davide 1*) -> Freigabe erzwingen
"""

BEISPIEL_BEWERTUNGEN = [
    # ---- 5 Sterne (mehrere, verschiedene Gründe) ----
    {
        "betrieb": "Da Davide (Restaurant, Bad Nauheim)",
        "sterne": 5,
        "text": (
            "Die Pizza war hervorragend und die hausgemachte Pasta ein Traum. "
            "Das Tiramisu zum Abschluss war das beste seit Langem. Wir kommen "
            "ganz sicher wieder."
        ),
    },
    {
        "betrieb": "Style of India (Restaurant, Bad Nauheim)",
        "sterne": 5,
        "text": (
            "Herzlicher Empfang und ein wunderbares Chicken Curry mit tollen "
            "Gewürzen. Man merkt die Liebe zum Detail. Absolute Empfehlung."
        ),
    },
    {
        "betrieb": "Tajine (Restaurant, Bad Nauheim)",
        "sterne": 5,
        "text": (
            "Authentische marokkanische Küche und ein sehr persönlicher, "
            "aufmerksamer Service. Die Lammtajine war zart und aromatisch. Ein "
            "rundum gelungener Abend."
        ),
    },
    {
        # Prüf-Fall: nennt Kellner "Stefan" -> Antwort darf den Namen NICHT nennen.
        "betrieb": "Deutsches Haus (Restaurant, Bad Nauheim)",
        "sterne": 5,
        "text": (
            "Gemütliche, traditionelle Gaststätte mit fairen Preisen. Unser "
            "Kellner Stefan war besonders freundlich und aufmerksam. Sehr gerne "
            "wieder!"
        ),
    },
    {
        "betrieb": "Zum Kastanienhof (Restaurant, Bad Nauheim)",
        "sterne": 5,
        "text": (
            "Super leckeres Essen zu fairen Preisen und eine gemütliche "
            "Atmosphäre. Das Personal war sehr zuvorkommend. Top!"
        ),
    },
    # ---- 4 Sterne ----
    {
        "betrieb": "La Trattoria (Restaurant, Bad Nauheim)",
        "sterne": 4,
        "text": (
            "Die Antipasti und die Pasta waren wirklich lecker. Nur die Preise "
            "sind etwas gehoben und wir mussten auf den Hauptgang recht lange "
            "warten. Insgesamt aber ein schöner Abend."
        ),
    },
    {
        "betrieb": "Café am Sprudelhof (Café, Bad Nauheim)",
        "sterne": 4,
        "text": (
            "Schöner Platz am Sprudelhof, guter Kuchen und freundliche "
            "Bedienung. An diesem Tag war es etwas voll und laut, aber der "
            "Kaffee war ausgezeichnet."
        ),
    },
    {
        "betrieb": "Zum Kastanienhof (Restaurant, Bad Nauheim)",
        "sterne": 4,
        "text": (
            "Das Chicken Curry hat gut geschmeckt und der Service war "
            "freundlich. Die Portionen könnten für den Preis etwas größer sein. "
            "Kommen aber gern wieder."
        ),
    },
    # ---- 3 Sterne ----
    {
        "betrieb": "Da Davide (Restaurant, Bad Nauheim)",
        "sterne": 3,
        "text": (
            "Die Pizza war lecker, aber es war sehr laut und voll, und wir "
            "haben lange auf die Bestellung gewartet. Schade, das Essen an sich "
            "war gut."
        ),
    },
    {
        "betrieb": "Deutsches Haus (Restaurant, Bad Nauheim)",
        "sterne": 3,
        "text": (
            "Das Schnitzel war ordentlich, aber der Service wirkte gestresst "
            "und wir wurden zwischendurch vergessen. Preis-Leistung geht in "
            "Ordnung."
        ),
    },
    # ---- 2 Sterne ----
    {
        "betrieb": "La Trattoria (Restaurant, Bad Nauheim)",
        "sterne": 2,
        "text": (
            "Leider enttäuschend: für die Preise hatte ich deutlich mehr "
            "erwartet, und wir haben uns beim Personal übersehen gefühlt. Die "
            "Pasta war zudem nur lauwarm."
        ),
    },
    {
        "betrieb": "Style of India (Restaurant, Bad Nauheim)",
        "sterne": 2,
        "text": (
            "Das Essen kam lauwarm an den Tisch und das Naan war trocken. "
            "Schade, wir hatten uns mehr erhofft."
        ),
    },
    # ---- 1 Stern ----
    {
        # Prüf-Fall: sachliche, ernste Beschwerde -> konkret eingehen, nichts versprechen.
        "betrieb": "Tajine (Restaurant, Bad Nauheim)",
        "sterne": 1,
        "text": (
            "In meinem Couscous war ein Haar, und als ich das Personal darauf "
            "ansprach, wurde kaum reagiert. So geht man nicht mit Gästen um."
        ),
    },
    {
        # Prüf-Fall: Risiko-Signalwörter -> Freigabe erzwingen, NICHT gegenkontern.
        "betrieb": "Da Davide (Restaurant, Bad Nauheim)",
        "sterne": 1,
        "text": (
            "Absolute Abzocke, die Rechnung war viel höher als die Karte. Das "
            "ist Betrug, ich denke über eine Anzeige nach."
        ),
    },

    # ---- Neue, realistische Alltags-Situationen (verschiedene Betriebe) ----
    {
        "betrieb": "Lieferservice Sonnenschein",
        "sterne": 5,
        "text": (
            "Online bestellt, pünktlich und noch heiß geliefert. Die Portionen "
            "waren großzügig und alles ordentlich verpackt. Gerne wieder!"
        ),
    },
    {
        "betrieb": "Restaurant Lindenhof",
        "sterne": 2,
        "text": (
            "Wir hatten einen Tisch reserviert und mussten trotzdem gut 20 "
            "Minuten warten, bis wir gesetzt wurden. Das Essen war okay, aber "
            "der Empfang war enttäuschend."
        ),
    },
    {
        "betrieb": "Restaurant Grüner Baum",
        "sterne": 5,
        "text": (
            "Ich habe eine Glutenunverträglichkeit und das Team hat mir super "
            "geholfen, passende Gerichte zu finden. Sehr aufmerksam und richtig "
            "lecker."
        ),
    },
    {
        "betrieb": "Familienrestaurant Anker",
        "sterne": 4,
        "text": (
            "Als Familie mit zwei kleinen Kindern haben wir uns sehr wohlgefühlt. "
            "Es gibt Hochstühle und eine Kinderkarte. Nur auf die Rechnung mussten "
            "wir etwas lange warten."
        ),
    },
    {
        "betrieb": "Bar & Küche Nova",
        "sterne": 3,
        "text": (
            "Das Essen war gut, aber die Musik war so laut, dass eine Unterhaltung "
            "kaum möglich war. Die Einrichtung ist ansonsten wirklich schön."
        ),
    },
    {
        "betrieb": "Gasthaus Adler",
        "sterne": 2,
        "text": (
            "Das Essen war in Ordnung, aber die Bedienung wirkte genervt und "
            "unfreundlich. Das trübt leider den Gesamteindruck."
        ),
    },
    {
        "betrieb": "Restaurant Belvedere",
        "sterne": 5,
        "text": (
            "Wir haben einen Geburtstag gefeiert und das Team hat spontan eine "
            "kleine Überraschung mit Kerze gezaubert. Eine tolle Geste!"
        ),
    },
    {
        "betrieb": "Bistro Ecke",
        "sterne": 2,
        "text": (
            "Die Vorspeise war klasse, aber der Hauptgang kam lauwarm. Er wurde "
            "auf Nachfrage aufgewärmt, aber der Moment war dahin."
        ),
    },
    {
        "betrieb": "Mittagstisch Kantine 7",
        "sterne": 4,
        "text": (
            "Faire Preise für gute Qualität, der Mittagstisch ist ein echtes "
            "Schnäppchen. Kleiner Minuspunkt: die Auswahl an vegetarischen "
            "Gerichten ist begrenzt."
        ),
    },
    {
        "betrieb": "Pizzeria Vulkan",
        "sterne": 2,
        "text": (
            "Wir haben zweimal die falsche Bestellung bekommen. Das Personal hat "
            "sich zwar entschuldigt, aber es hat den ganzen Abend verzögert."
        ),
    },
    {
        "betrieb": "Café Alt-Wien",
        "sterne": 5,
        "text": (
            "Seit Jahren Stammgäste und nie enttäuscht. Gleichbleibend hohe "
            "Qualität und immer ein herzlicher Empfang."
        ),
    },
    {
        # Prüf-Fall: harscher Ton + Risikowort (Gesundheitsamt) -> ruhig, nicht gegenkontern.
        "betrieb": "Restaurant Panorama",
        "sterne": 1,
        "text": (
            "Absolute Frechheit, das Essen war kaum genießbar und die Bedienung "
            "patzig. Ich überlege, das Gesundheitsamt zu informieren."
        ),
    },
]
