/* Kudora Content-Script.
 *
 * Läuft auf der Google-Bewertungsseite: findet Bewertungs-Karten, blendet pro
 * Karte einen "✨ Mit Kudora antworten"-Knopf ein, liest Text + Sterne, holt vom
 * Backend eine Antwort und schreibt sie ins Google-Antwortfeld. Der Mensch prüft
 * und klickt SELBST Googles "Senden" (assistierend, kein Auto-Post).
 *
 * Testbar ohne Erweiterung: ist `window.__KUDORA_GENERATE__` gesetzt (Testseite),
 * wird diese Funktion statt des Hintergrund-Fetch genutzt.
 */
(function () {
  "use strict";

  const S = window.KUDORA_SELECTORS || {};
  const MARK = "data-kudora-done";

  /* ---------- kleine Helfer ---------- */

  function firstMatch(root, liste) {
    for (const sel of liste || []) {
      try {
        const el = root.querySelector(sel);
        if (el) return el;
      } catch (_) {
        /* ungültiger Selektor -> überspringen */
      }
    }
    return null;
  }

  function alleKarten() {
    const menge = new Set();
    for (const sel of S.card || []) {
      try {
        document.querySelectorAll(sel).forEach((e) => menge.add(e));
      } catch (_) {
        /* überspringen */
      }
    }
    return [...menge];
  }

  function clampSterne(n) {
    n = parseInt(n, 10);
    if (isNaN(n)) return 5;
    return Math.min(5, Math.max(1, n));
  }

  function leseText(karte) {
    const el = firstMatch(karte, S.text);
    return ((el ? el.textContent : karte.textContent) || "").trim();
  }

  function leseSterne(karte) {
    const el = firstMatch(karte, S.stars) || karte;
    if (el.getAttribute) {
      const direkt = el.getAttribute("data-kudora-stars-value");
      if (direkt) return clampSterne(direkt);
      const label = el.getAttribute("aria-label") || "";
      const m = label.match(/(\d)(?:[.,]\d)?\s*(?:von|\/|out of)?\s*5/i);
      if (m) return clampSterne(m[1]);
      const m2 = label.match(/(\d)/);
      if (m2) return clampSterne(m2[1]);
    }
    return 5;
  }

  /* Setzt den Wert so, dass auch von Google/React kontrollierte Felder es merken. */
  function setzeFeldwert(el, wert) {
    const proto =
      el.tagName === "TEXTAREA"
        ? window.HTMLTextAreaElement.prototype
        : window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value");
    if (setter && setter.set) setter.set.call(el, wert);
    else el.value = wert;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  /* ---------- Backend-Aufruf (mit Test-Weiche) ---------- */

  function holeAntwort(payload) {
    if (typeof window.__KUDORA_GENERATE__ === "function") {
      return Promise.resolve(window.__KUDORA_GENERATE__(payload));
    }
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
      return new Promise((resolve) => {
        chrome.runtime.sendMessage(
          { type: "kudora-fetch", path: "/api/antwort", body: payload },
          (resp) => {
            if (resp && resp.ok) resolve(resp.data);
            else
              resolve({
                ok: false,
                fehler: "netzwerk",
                meldung:
                  (resp && resp.error) ||
                  "Keine Verbindung zum Kudora-Server. Läuft das Backend?",
              });
          }
        );
      });
    }
    return Promise.resolve({
      ok: false,
      fehler: "nicht_verfuegbar",
      meldung: "Kudora-Hintergrund nicht verfügbar.",
    });
  }

  /* Speichert die finale Antwort -> Kudora lernt den Stil fürs nächste Mal. */
  function sendeFreigabe(payload) {
    if (typeof window.__KUDORA_FREIGABE__ === "function") {
      return Promise.resolve(window.__KUDORA_FREIGABE__(payload));
    }
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
      return new Promise((resolve) => {
        chrome.runtime.sendMessage(
          { type: "kudora-fetch", path: "/api/freigabe", body: payload },
          (resp) => resolve(resp && resp.ok ? resp.data : { ok: false })
        );
      });
    }
    return Promise.resolve({ ok: false });
  }

  /* ---------- UI ---------- */

  function knopfStatus(btn, zustand, text) {
    btn.classList.remove("kudora-laden", "kudora-fehler", "kudora-fertig");
    if (zustand === "laden") {
      btn.classList.add("kudora-laden");
      btn.disabled = true;
      btn.textContent = "✨ Kudora schreibt …";
    } else if (zustand === "fehler") {
      btn.classList.add("kudora-fehler");
      btn.disabled = false;
      btn.textContent = "⚠ Nochmal versuchen";
      if (text) btn.title = text;
    } else if (zustand === "fertig") {
      btn.classList.add("kudora-fertig");
      btn.disabled = false;
      btn.textContent = "↻ Neue Formulierung";
    } else {
      btn.disabled = false;
      btn.textContent = "✨ Mit Kudora antworten";
    }
  }

  function zeigeHinweis(karte) {
    if (karte.querySelector(".kudora-hinweis")) return;
    const h = document.createElement("div");
    h.className = "kudora-hinweis";
    h.textContent =
      "Heikle Bewertung – bitte die Antwort kurz prüfen, bevor Sie sie senden.";
    karte.appendChild(h);
  }

  /* Fallback, falls kein Antwortfeld gefunden wird: schwebendes Panel. */
  function zeigePanel(text) {
    let panel = document.getElementById("kudora-panel");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "kudora-panel";
      panel.innerHTML =
        '<div class="kudora-panel-kopf">Kudora-Antwort' +
        '<span class="kudora-panel-zu">✕</span></div>' +
        '<textarea class="kudora-panel-text" rows="5"></textarea>' +
        '<button class="kudora-panel-copy" type="button">In Zwischenablage</button>';
      document.body.appendChild(panel);
      panel.querySelector(".kudora-panel-zu").addEventListener("click", () => {
        panel.style.display = "none";
      });
      panel.querySelector(".kudora-panel-copy").addEventListener("click", () => {
        const t = panel.querySelector(".kudora-panel-text").value;
        if (navigator.clipboard) navigator.clipboard.writeText(t);
        const b = panel.querySelector(".kudora-panel-copy");
        b.textContent = "✓ Kopiert";
        setTimeout(() => (b.textContent = "In Zwischenablage"), 1500);
      });
    }
    panel.style.display = "block";
    panel.querySelector(".kudora-panel-text").value = text;
  }

  async function aufGenerieren(karte, btn) {
    const original = leseText(karte);
    if (!original) {
      knopfStatus(btn, "fehler", "Kein Bewertungstext gefunden.");
      return;
    }
    knopfStatus(btn, "laden");
    const res = await holeAntwort({ original, sterne: leseSterne(karte), betrieb: "" });
    if (!res || res.ok === false) {
      knopfStatus(btn, "fehler", (res && res.meldung) || "Fehler.");
      return;
    }
    const entwurf = (res.entwurf || "").trim();
    const feld = firstMatch(karte, S.reply) || firstMatch(document, S.reply);
    if (feld) {
      setzeFeldwert(feld, entwurf);
      feld.focus();
    } else {
      zeigePanel(entwurf);
    }
    if (res.freigabe_noetig || (res.risikowoerter && res.risikowoerter.length)) {
      zeigeHinweis(karte);
    }
    knopfStatus(btn, "fertig");
    fuegeMerkenKnopf(btn.parentNode, {
      original,
      sterne: leseSterne(karte),
      entwurf,
      feld,
    });
  }

  /* "Übernehmen & merken": speichert die (evtl. angepasste) finale Antwort,
   * damit Kudora den Stil des Betriebs lernt. Der Wirt sendet danach wie gewohnt
   * selbst über Googles eigenen Senden-Knopf. */
  function fuegeMerkenKnopf(leiste, ctx) {
    if (!leiste || leiste.querySelector(".kudora-merken")) return;
    const m = document.createElement("button");
    m.type = "button";
    m.className = "kudora-merken";
    m.textContent = "✓ Übernehmen & merken";
    m.title = "Speichert Ihre finale Antwort, damit Kudora Ihren Stil lernt.";
    m.addEventListener("click", async () => {
      const finale = ctx.feld ? ctx.feld.value : ctx.entwurf;
      m.disabled = true;
      m.textContent = "… speichert";
      const res = await sendeFreigabe({
        original: ctx.original,
        sterne: ctx.sterne,
        betrieb: "",
        entwurf: ctx.entwurf,
        finale_antwort: finale,
      });
      m.textContent = res && res.ok ? "✓ Gemerkt" : "⚠ Fehler";
      setTimeout(() => {
        m.disabled = false;
      }, 1400);
    });
    leiste.appendChild(m);
  }

  function injiziereKnopf(karte) {
    if (karte.getAttribute(MARK)) return;
    karte.setAttribute(MARK, "1");
    const leiste = document.createElement("div");
    leiste.className = "kudora-bar";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "kudora-btn";
    btn.textContent = "✨ Mit Kudora antworten";
    btn.addEventListener("click", () => aufGenerieren(karte, btn));
    leiste.appendChild(btn);
    karte.appendChild(leiste);
  }

  /* ---------- Scannen (auch bei nachgeladenen Bewertungen) ---------- */

  function scanne() {
    alleKarten().forEach(injiziereKnopf);
  }

  function debounce(fn, ms) {
    let t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }

  function init() {
    scanne();
    if (document.body) {
      const obs = new MutationObserver(debounce(scanne, 400));
      obs.observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Für Tests nach außen geben (harmlos in Produktion).
  window.__KUDORA__ = { scanne, leseText, leseSterne };
})();
