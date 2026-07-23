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
  // Das Antwortfeld des Betriebs (z. B. business.google.com). Bewusst nur
  // SPEZIFISCHE Felder — kein blankes "textarea", sonst würde auf Google Maps
  // ein fremdes Feld getroffen. Findet sich keins, zeigt Kudora die Antwort
  // direkt unter der Bewertung an.
  reply: [
    "[data-kudora-reply]",
    'textarea[aria-label*="ffentlich"]',
    'textarea[aria-label*="Antwort"]',
    'textarea[aria-label*="antworten"]',
    'textarea[aria-label*="reply"]',
    'textarea[aria-label*="Reply"]',
    '[role="dialog"] textarea',
  ],
  // Googles eigener "Senden/Posten"-Knopf der Antwort (nur im Inhaber-Profil da).
  // Bewusst innerhalb der Karte gesucht, damit kein fremder Knopf getroffen wird.
  send: [
    "[data-kudora-send]",
    'button[aria-label*="Antwort senden"]',
    'button[aria-label*="Antwort posten"]',
    'button[aria-label*="Antwort veröffentlichen"]',
    'button[aria-label*="Senden"]',
    'button[aria-label*="Posten"]',
    'button[aria-label*="Reply"]',
    'button[jsaction*="reply"]',
  ],
  // "Antworten"-Knopf/Link, den nur der Inhaber sieht (öffnet das Antwortfeld).
  // Dient als Signal "hier kann man antworten" — nur DANN zeigt Kudora sich.
  replyTrigger: [
    "[data-kudora-reply-trigger]",
    'button[aria-label*="Antworten"]',
    'button[aria-label*="antworten"]',
    'button[aria-label*="Reply"]',
    'button[aria-label*="reply"]',
    'a[aria-label*="Antworten"]',
  ],
  // Vorhandene Inhaber-Antwort (dann ist die Bewertung schon beantwortet ->
  // Kudora zeigt sich NICHT). Zusätzlich wird im Code auf den Text geprüft.
  ownerReply: ["[data-kudora-owner-reply]"],
};
