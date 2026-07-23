/* Kudora Service Worker (MV3).
 *
 * Führt die Netzwerk-Aufrufe zum Kudora-Backend aus. Das passiert bewusst hier
 * im Hintergrund (nicht im Seiten-Kontext), damit CORS/Mixed-Content-Regeln der
 * Google-Seite nicht stören und der Backend-Zugriff an einer Stelle liegt.
 */

// Feste Konfiguration (Server-Adresse + Token) aus config.js laden.
importScripts("config.js");
const CFG = self.KUDORA_CONFIG || {};
const STANDARD_URL = CFG.backendUrl || "http://localhost:8000";
const TOKEN = CFG.token || "";

async function holeConfig() {
  // Eine im Popup gesetzte Adresse hat Vorrang; sonst der Wert aus config.js.
  const gespeichert = await chrome.storage.sync.get(["backendUrl", "enabled"]);
  const backendUrl = (gespeichert.backendUrl || STANDARD_URL).replace(/\/+$/, "");
  const enabled = gespeichert.enabled !== false; // Standard: an
  return { backendUrl, enabled };
}

function kopfzeilen(mitJson) {
  const h = {};
  if (mitJson) h["Content-Type"] = "application/json";
  if (TOKEN) h["X-Kudora-Token"] = TOKEN; // Schutz gegen Fremdzugriff
  return h;
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  // 1) Antwort/Freigabe an das Backend weiterreichen.
  if (msg && msg.type === "kudora-fetch") {
    holeConfig().then(async ({ backendUrl }) => {
      try {
        const res = await fetch(backendUrl + msg.path, {
          method: "POST",
          headers: kopfzeilen(true),
          body: JSON.stringify(msg.body || {}),
        });
        sendResponse({ ok: true, data: await res.json() });
      } catch (e) {
        sendResponse({ ok: false, error: String(e) });
      }
    });
    return true; // asynchrone Antwort
  }

  // 2) Health-Check (fürs Popup: läuft der Server?).
  if (msg && msg.type === "kudora-health") {
    holeConfig().then(async ({ backendUrl }) => {
      try {
        const res = await fetch(backendUrl + "/", { headers: kopfzeilen(false) });
        sendResponse({ ok: true, data: await res.json() });
      } catch (e) {
        sendResponse({ ok: false, error: String(e) });
      }
    });
    return true;
  }
});
