/* Popup-Logik: Backend-Adresse speichern, An/Aus, Server-Status prüfen. */

const STANDARD_URL =
  (self.KUDORA_CONFIG && self.KUDORA_CONFIG.backendUrl) || "http://localhost:8000";

const urlFeld = document.getElementById("url");
const enabledFeld = document.getElementById("enabled");
const statusEl = document.getElementById("status");

function setzeStatus(text, klasse) {
  statusEl.textContent = text;
  statusEl.className = "status" + (klasse ? " " + klasse : "");
}

// Gespeicherte Werte laden.
chrome.storage.sync.get(["backendUrl", "enabled"], (v) => {
  urlFeld.value = v.backendUrl || STANDARD_URL;
  enabledFeld.checked = v.enabled !== false;
});

function pruefe() {
  setzeStatus("Prüfe Verbindung …");
  chrome.runtime.sendMessage({ type: "kudora-health" }, (resp) => {
    if (resp && resp.ok) {
      const modell = (resp.data && resp.data.modell) || "?";
      setzeStatus("Verbunden ✓  (Modell: " + modell + ")", "ok");
    } else {
      setzeStatus("Keine Verbindung — läuft das Backend?", "fehler");
    }
  });
}

document.getElementById("speichern").addEventListener("click", () => {
  const backendUrl = (urlFeld.value || STANDARD_URL).trim().replace(/\/+$/, "");
  const enabled = enabledFeld.checked;
  chrome.storage.sync.set({ backendUrl, enabled }, () => {
    urlFeld.value = backendUrl;
    pruefe();
  });
});

// Beim Öffnen direkt den Status prüfen.
pruefe();
