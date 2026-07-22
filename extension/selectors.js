/* Alle DOM-Selektoren der Google-Bewertungsseite an EINER Stelle.
 *
 * WICHTIG: Googles Oberfläche ist nicht öffentlich dokumentiert und ändert sich.
 * Wenn der Kudora-Knopf einmal nicht mehr erscheint oder das falsche Feld füllt,
 * müssen hier nur die Selektoren angepasst werden — sonst nichts.
 *
 * Reihenfolge = Priorität: Der erste Treffer gewinnt. Ganz vorn stehen die
 * `data-kudora-*`-Attribute (nutzt die lokale Testseite), danach mehrere
 * plausible Kandidaten für die echte Google-Seite. Beim Live-Abgleich
 * (eingeloggt) ergänzt man den tatsächlich passenden Selektor einfach vorne.
 */
window.KUDORA_SELECTORS = {
  // Eine einzelne Bewertungs-Karte.
  card: [
    "[data-kudora-review]",
    "div[data-review-id]",
    "div[data-google-review-id]",
    ".gws-localreviews__general-reviews-block .WMbnJf",
    "div.jftiEf",
  ],
  // Der Bewertungstext innerhalb einer Karte.
  text: [
    "[data-kudora-text]",
    ".review-full-text",
    "span[data-expandable-section]",
    ".wiI7pd",
    ".MyEned",
  ],
  // Element mit der Sternzahl (meist per aria-label, z. B. "5 von 5 Sternen").
  stars: [
    "[data-kudora-stars]",
    'span[aria-label*="Stern"]',
    'span[aria-label*="star"]',
    'g-review-stars span',
    ".kvMYJc",
  ],
  // Das Antwortfeld des Betriebs.
  reply: [
    "[data-kudora-reply]",
    'textarea[aria-label*="Antwort"]',
    'textarea[aria-label*="antworten"]',
    'textarea[aria-label*="reply"]',
    'textarea[aria-label*="Reply"]',
    "textarea",
  ],
};
