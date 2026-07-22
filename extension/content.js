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

  // Phrasen, die eine bereits vorhandene Inhaber-Antwort anzeigen.
  const INHABER_PHRASEN = [
    "antwort vom inhaber",
    "antwort des inhabers",
    "response from the owner",
    "owner's response",
    "reply from the owner",
  ];

  /* Ist die Bewertung schon (vom Inhaber) beantwortet? Dann zeigt Kudora sich nicht. */
  function istBeantwortet(karte) {
    if (firstMatch(karte, S.ownerReply)) return true;
    const t = (karte.textContent || "").toLowerCase();
    return INHABER_PHRASEN.some((p) => t.includes(p));
  }

  /* Kann man hier überhaupt antworten? (eigenes Profil = Antwortfeld ODER
   * ein "Antworten"-Knopf vorhanden). Sonst zeigt Kudora sich nicht. */
  function kannAntworten(karte) {
    return !!(firstMatch(karte, S.reply) || firstMatch(karte, S.replyTrigger));
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

  /* Ist die Verbindung zur Erweiterung noch gültig? Nach einem Erweiterungs-
   * Neuladen (↻) verliert ein bereits offenes Tab den Kontext ("Extension
   * context invalidated"). Dann NICHT senden, sondern sauber melden. */
  function kontextGueltig() {
    try {
      return !!(typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.id);
    } catch (_) {
      return false;
    }
  }

  /* Sichere Nachricht an den Hintergrund — wirft nie, meldet Fehler als Objekt. */
  function sendeNachricht(msg) {
    return new Promise((resolve) => {
      if (!kontextGueltig()) {
        resolve({
          ok: false,
          error:
            "Erweiterung wurde neu geladen — bitte diese Google-Seite einmal neu " +
            "laden (Cmd+R).",
        });
        return;
      }
      try {
        chrome.runtime.sendMessage(msg, (resp) => {
          const err = chrome.runtime && chrome.runtime.lastError;
          if (err) {
            resolve({ ok: false, error: err.message });
            return;
          }
          resolve(resp || { ok: false, error: "Keine Antwort vom Hintergrund." });
        });
      } catch (e) {
        resolve({ ok: false, error: String(e) });
      }
    });
  }

  async function holeAntwort(payload) {
    if (typeof window.__KUDORA_GENERATE__ === "function") {
      return window.__KUDORA_GENERATE__(payload);
    }
    const resp = await sendeNachricht({
      type: "kudora-fetch",
      path: "/api/antwort",
      body: payload,
    });
    if (resp && resp.ok) return resp.data;
    return {
      ok: false,
      fehler: "netzwerk",
      meldung:
        (resp && resp.error) ||
        "Keine Verbindung zum Kudora-Server. Läuft das Backend?",
    };
  }

  /* Speichert die finale Antwort -> Kudora lernt den Stil fürs nächste Mal. */
  async function sendeFreigabe(payload) {
    if (typeof window.__KUDORA_FREIGABE__ === "function") {
      return window.__KUDORA_FREIGABE__(payload);
    }
    const resp = await sendeNachricht({
      type: "kudora-fetch",
      path: "/api/freigabe",
      body: payload,
    });
    return resp && resp.ok ? resp.data : { ok: false };
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

  function entferneHinweis(karte) {
    const h = karte.querySelector(".kudora-hinweis");
    if (h) h.remove();
  }

  /* Zeigt ein EDITIERBARES Antwortfeld direkt unter der Bewertung, wenn Google
   * selbst keins anbietet (z. B. fremde Betriebe / Google Maps). Der Nutzer kann
   * den Text ändern. Senden ist hier nicht möglich (dazu unten der Hinweis). */
  function zeigeInlineAntwort(leiste, text) {
    let box =
      leiste.nextElementSibling &&
      leiste.nextElementSibling.classList.contains("kudora-antwortbox")
        ? leiste.nextElementSibling
        : null;
    if (!box) {
      box = document.createElement("div");
      box.className = "kudora-antwortbox";
      const ta = document.createElement("textarea");
      ta.className = "kudora-antwort-text";
      ta.rows = 4;
      box.appendChild(ta);
      leiste.insertAdjacentElement("afterend", box);
    }
    const ta = box.querySelector(".kudora-antwort-text");
    ta.value = text;
    return ta;
  }

  function zeigeSendeHinweis(karte) {
    if (karte.querySelector(".kudora-sende-hinweis")) return;
    const h = document.createElement("div");
    h.className = "kudora-sende-hinweis";
    h.textContent =
      "Direktes Senden geht nur in Ihrem eigenen Unternehmensprofil " +
      "(business.google.com, mit dem verwaltenden Konto). Hier können Sie die " +
      "Antwort nur ansehen und anpassen.";
    karte.appendChild(h);
  }

  function entferneSendeHinweis(karte) {
    const h = karte.querySelector(".kudora-sende-hinweis");
    if (h) h.remove();
  }

  /* Aktuelle (evtl. vom Nutzer geänderte) Antwort aus Google-Feld oder Inline-Box. */
  function aktuelleAntwort(ctx) {
    if (ctx.feld) return ctx.feld.value;
    if (ctx.box) return ctx.box.value;
    return ctx.entwurf;
  }

  /* "✓ Senden": lernt aus der finalen Antwort (auch wenn geändert) und klickt
   * Googles eigenen Senden-Knopf. Findet Kudora den nicht, fügt es die Antwort
   * ein und bittet, Googles Knopf selbst zu klicken. */
  async function aufSenden(ctx, sendBtn) {
    const finale = (aktuelleAntwort(ctx) || "").trim();
    if (!finale) return;
    // Lernen: JEDE gesendete Antwort (auch geänderte) macht Kudora besser.
    sendeFreigabe({
      original: ctx.original,
      sterne: ctx.sterne,
      betrieb: "",
      entwurf: ctx.entwurf,
      finale_antwort: finale,
    });
    const googleSenden = firstMatch(ctx.karte, S.send);
    if (ctx.feld && googleSenden) {
      setzeFeldwert(ctx.feld, finale);
      googleSenden.click();
      sendBtn.disabled = true;
      sendBtn.textContent = "✓ Gesendet";
    } else {
      // Konnte Googles Senden-Knopf nicht sicher finden -> Nutzer klickt selbst.
      if (ctx.feld) {
        setzeFeldwert(ctx.feld, finale);
        ctx.feld.focus();
      }
      sendBtn.textContent = "Jetzt in Google senden";
      sendBtn.title =
        "Kudora hat die Antwort eingefügt und daraus gelernt. Bitte klicken Sie " +
        "nun Googles eigenen Senden-Knopf.";
    }
  }

  /* Baut/aktualisiert den "Senden"-Knopf in der Leiste — nur wenn ein echtes
   * Google-Antwortfeld existiert (sonst kann man nicht senden). */
  function aktualisiereSendenKnopf(leiste, ctx) {
    let sendBtn = leiste.querySelector(".kudora-senden");
    if (ctx.feld) {
      entferneSendeHinweis(ctx.karte);
      if (!sendBtn) {
        sendBtn = document.createElement("button");
        sendBtn.type = "button";
        sendBtn.className = "kudora-senden";
        sendBtn.addEventListener("click", () => aufSenden(sendBtn._ctx, sendBtn));
        leiste.appendChild(sendBtn);
      }
      sendBtn.disabled = false;
      sendBtn.textContent = "✓ Senden";
      sendBtn._ctx = ctx;
    } else {
      // Kein Antwortfeld (fremdes Profil / Maps) -> kein Senden möglich.
      if (sendBtn) sendBtn.remove();
      zeigeSendeHinweis(ctx.karte);
    }
  }

  async function aufGenerieren(karte, btn) {
    const leiste = btn.parentNode;
    const original = leseText(karte);
    if (!original) {
      knopfStatus(btn, "fehler", "Kein Bewertungstext gefunden.");
      return;
    }
    const sterne = leseSterne(karte);
    knopfStatus(btn, "laden");
    const res = await holeAntwort({ original, sterne, betrieb: "" });
    if (!res || res.ok === false) {
      knopfStatus(btn, "fehler", (res && res.meldung) || "Fehler.");
      return;
    }
    const entwurf = (res.entwurf || "").trim();

    // Antwortfeld der eigenen Bewertung finden. Fehlt es, aber es gibt einen
    // "Antworten"-Knopf (Inhaber-Ansicht), diesen klicken, um Googles Feld zu
    // öffnen, kurz warten und erneut suchen. WICHTIG: nur INNERHALB der Karte.
    let feld = firstMatch(karte, S.reply);
    if (!feld) {
      const ausloeser = firstMatch(karte, S.replyTrigger);
      if (ausloeser) {
        ausloeser.click();
        await new Promise((r) => setTimeout(r, 350));
        feld = firstMatch(karte, S.reply);
      }
    }
    let box = null;
    if (feld) {
      setzeFeldwert(feld, entwurf);
      feld.focus();
    } else {
      box = zeigeInlineAntwort(leiste, entwurf);
    }

    // Hinweis NUR bei heiklen Fällen: schlechte (≤3 Sterne) ODER riskante.
    const heikel = (res.risikowoerter && res.risikowoerter.length > 0) || sterne <= 3;
    if (heikel) zeigeHinweis(karte);
    else entferneHinweis(karte);

    knopfStatus(btn, "fertig"); // Knopf wird zu "↻ Neue Formulierung"
    aktualisiereSendenKnopf(leiste, { karte, original, sterne, entwurf, feld, box });
  }

  function injiziereKnopf(karte) {
    if (karte.getAttribute(MARK)) return;
    // Dopplung vermeiden: verschachtelte Karten (Google-Layout matcht mehrere
    // Ebenen) sollen nur EINEN Knopf bekommen.
    if (karte.querySelector(".kudora-bar")) return; // ein Nachfahre hat schon einen
    if (karte.parentElement && karte.parentElement.closest("[" + MARK + "]")) return;

    // NUR unbeantwortete Bewertungen, und nur wo man wirklich antworten kann
    // (eigenes Unternehmensprofil). Sonst zeigt Kudora sich gar nicht.
    if (istBeantwortet(karte)) return;
    if (!kannAntworten(karte)) return;

    karte.setAttribute(MARK, "1");
    const leiste = document.createElement("div");
    leiste.className = "kudora-bar";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "kudora-btn";
    btn.textContent = "✨ Mit Kudora antworten";
    btn.addEventListener("click", () => {
      // Niemals einen unbehandelten Fehler in die Konsole/Chrome werfen.
      Promise.resolve()
        .then(() => aufGenerieren(karte, btn))
        .catch((e) => knopfStatus(btn, "fehler", String(e)));
    });
    leiste.appendChild(btn);
    karte.appendChild(leiste);
  }

  /* ---------- Scannen (auch bei nachgeladenen Bewertungen) ---------- */

  function scanne() {
    try {
      alleKarten().forEach((karte) => {
        try {
          injiziereKnopf(karte);
        } catch (_) {
          /* eine kaputte Karte darf den Rest nicht stoppen */
        }
      });
    } catch (_) {
      /* Scan-Fehler schlucken -> nie roter Erweiterungs-Fehler */
    }
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
