"""Stil-Bibliothek: menschlich klingende Muster-Antworten als Grund-Vorbild.

Diese Beispiele werden dem Modell als Vorbild mitgegeben, damit die Antworten von
Anfang an natürlich klingen (nicht formelhaft). Sie zeigen: abwechslungsreiche
Anfänge (nicht immer „Vielen Dank …"), kurz (2–3 Sätze), warm, souverän — und bei
Kritik ruhig, ohne zu streiten, mit Verweis auf direkten Kontakt.

Alles synthetisch, keine echten Kundendaten. Struktur wie das Protokoll
(betrieb/sterne/original/finale_antwort), damit es in die gleiche Few-Shot-Logik passt.
"""

STIL_BEISPIELE = [
    # ---------- positiv ----------
    {
        "betrieb": "Restaurant",
        "sterne": 5,
        "original": "Fantastisches Essen, wir haben den Abend sehr genossen.",
        "finale_antwort": (
            "Das freut uns riesig zu lesen — genau dafür stehen wir jeden Abend "
            "am Herd. Wir sehen uns hoffentlich bald wieder bei Ihnen."
        ),
    },
    {
        "betrieb": "Restaurant",
        "sterne": 5,
        "original": "Das Rinderfilet war perfekt auf den Punkt, ein Traum.",
        "finale_antwort": (
            "Beim Filet sind wir besonders pingelig, umso schöner, dass es genau "
            "Ihren Geschmack getroffen hat. Kommen Sie gut wieder!"
        ),
    },
    {
        "betrieb": "Hotel",
        "sterne": 5,
        "original": "Herzlicher Empfang und ein wunderschönes Zimmer.",
        "finale_antwort": (
            "Ein guter Empfang liegt uns wirklich am Herzen — danke für die schönen "
            "Worte. Wir freuen uns schon auf Ihren nächsten Besuch."
        ),
    },
    {
        # Bewertung nennt einen Mitarbeiter -> Antwort nennt KEINEN Namen.
        "betrieb": "Restaurant",
        "sterne": 5,
        "original": "Der Kellner Thomas war ein Traum, so aufmerksam!",
        "finale_antwort": (
            "So ein Lob geben wir sehr gern ans ganze Team weiter — schön, dass Sie "
            "sich bei uns so gut aufgehoben gefühlt haben. Bis bald!"
        ),
    },
    {
        "betrieb": "Café",
        "sterne": 5,
        "original": "Bester Kuchen weit und breit!",
        "finale_antwort": (
            "Über so ein Lob für unseren Kuchen freuen wir uns sehr — da steckt viel "
            "Herzblut drin. Bis zum nächsten Stück!"
        ),
    },
    # ---------- gemischt ----------
    {
        "betrieb": "Restaurant",
        "sterne": 4,
        "original": "Essen top, nur die Wartezeit war lang.",
        "finale_antwort": (
            "Schön, dass es geschmeckt hat! Die Wartezeit ärgert uns selbst — an "
            "vollen Abenden arbeiten wir daran, schneller zu werden. Danke, dass Sie "
            "trotzdem geblieben sind."
        ),
    },
    {
        "betrieb": "Restaurant",
        "sterne": 3,
        "original": "War okay, hat mich aber nicht umgehauen.",
        "finale_antwort": (
            "Danke für die ehrliche Einschätzung. Ein bloßes Okay ist uns ehrlich "
            "gesagt zu wenig — beim nächsten Mal würden wir Sie gern richtig überzeugen."
        ),
    },
    {
        "betrieb": "Café",
        "sterne": 3,
        "original": "Kaffee gut, aber es war viel zu laut.",
        "finale_antwort": (
            "Freut uns, dass der Kaffee gepasst hat. Dass es an dem Tag zu laut war, "
            "nehmen wir mit — an vollen Nachmittagen ist das leider manchmal so."
        ),
    },
    # ---------- negativ ----------
    {
        "betrieb": "Restaurant",
        "sterne": 2,
        "original": "Die Pasta war lauwarm und versalzen.",
        "finale_antwort": (
            "Das tut uns leid, so soll kein Teller unser Haus verlassen. Wir geben "
            "das direkt in die Küche weiter und würden uns freuen, es besser zu machen."
        ),
    },
    {
        "betrieb": "Restaurant",
        "sterne": 2,
        "original": "Wir haben uns komplett übersehen gefühlt.",
        "finale_antwort": (
            "Das hören wir gar nicht gern, denn aufmerksamer Service ist uns wichtig. "
            "Danke, dass Sie es ansprechen — wir schauen uns das intern genau an."
        ),
    },
    {
        "betrieb": "Hotel",
        "sterne": 1,
        "original": "Das Zimmer war nicht sauber, das geht gar nicht.",
        "finale_antwort": (
            "Das ist ärgerlich und entspricht überhaupt nicht unserem Standard. Bitte "
            "melden Sie sich einmal kurz direkt bei uns — wir möchten das nachvollziehen "
            "und in Ordnung bringen."
        ),
    },
    {
        # Vorwurf -> NICHT gegenkontern, ruhig, Klärung im direkten Kontakt.
        "betrieb": "Restaurant",
        "sterne": 1,
        "original": "Totale Abzocke, die Rechnung war viel zu hoch!",
        "finale_antwort": (
            "Das überrascht uns, denn unsere Preise stehen offen auf der Karte. Damit "
            "wir das gemeinsam klären können, melden Sie sich bitte einmal direkt bei "
            "uns — das lässt sich sicher aufklären."
        ),
    },
]
