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
    // Antwortfeld ODER ein "Antworten"-Knopf (Text-basiert erkannt) in der Karte.
    return !!(firstMatch(karte, S.reply) || findeTrigger(karte));
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

  // Ist das Feld ein bearbeitbares div (contenteditable / role=textbox)?
  function istEditierbar(el) {
    return !!(
      el &&
      (el.isContentEditable ||
        el.getAttribute("contenteditable") === "true" ||
        el.getAttribute("role") === "textbox")
    );
  }

  /* Setzt den Wert so, dass auch von Google/React kontrollierte Felder es merken —
   * funktioniert für <textarea>/<input> UND für bearbeitbare div-Felder. */
  function setzeFeldwert(el, wert) {
    if (istEditierbar(el) && el.tagName !== "TEXTAREA" && el.tagName !== "INPUT") {
      el.focus();
      el.textContent = wert;
      el.dispatchEvent(new InputEvent("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      return;
    }
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

  // Aktueller Text eines Feldes (Textarea/Input ODER bearbeitbares div).
  function feldWert(el) {
    if (!el) return "";
    if (typeof el.value === "string" && el.tagName !== "DIV") return el.value;
    return el.innerText || el.textContent || "";
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

  /* ---------- Googles Antwort-Fenster ("Auf Rezension antworten") ---------- */

  // Kontext der zuletzt per Kudora angeklickten Bewertung (voller Text + Sterne),
  // damit das Modal daraus generiert (statt aus dem gekürzten Modal-Text).
  let modalKontext = null;

  const TRIGGER_WOERTER = ["antworten", "reply"];
  const SUBMIT_WOERTER = ["antworten", "senden", "posten", "reply", "send", "post"];

  // Nur Buchstaben, klein — so matcht "↩ Antworten" == "antworten", aber
  // "Öffentlich antworten" (das Textfeld-Label) NICHT.
  function normText(el) {
    const roh =
      (el.getAttribute && el.getAttribute("aria-label")) || el.textContent || "";
    return roh.toLowerCase().replace(/[^a-zäöüß]/g, "");
  }

  // Googles "Antworten"-Knopf einer Karte (öffnet das Antwort-Fenster).
  function findeTrigger(karte) {
    const els = karte.querySelectorAll('button,[role="button"],a');
    for (const el of els) if (TRIGGER_WOERTER.includes(normText(el))) return el;
    return firstMatch(karte, S.replyTrigger);
  }

  // Ein bearbeitbares Feld innerhalb eines Bereichs finden (Textarea/Input/div).
  function findeFeldIn(root) {
    return (
      root.querySelector('textarea[aria-label*="ffentlich" i]') ||
      root.querySelector('[contenteditable="true"][aria-label*="ffentlich" i]') ||
      root.querySelector('[role="textbox"][aria-label*="ffentlich" i]') ||
      root.querySelector("textarea") ||
      root.querySelector('[contenteditable="true"]') ||
      root.querySelector('[role="textbox"]') ||
      root.querySelector('input[type="text"]')
    );
  }

  // Kleinsten Container finden, dessen Überschrift/Text die Phrase enthält und
  // der ein bearbeitbares Feld besitzt (für Googles Antwort-Fenster).
  function findeContainerMitText(phrase) {
    const els = document.querySelectorAll("h1,h2,h3,div,span");
    for (const el of els) {
      const t = (el.textContent || "").trim().toLowerCase();
      if (t === phrase || t.startsWith(phrase)) {
        let p = el;
        for (let i = 0; i < 7 && p; i++) {
          if (findeFeldIn(p)) return p;
          p = p.parentElement;
        }
      }
    }
    return null;
  }

  /* Das offene Antwort-Fenster ("Auf Rezension antworten") + sein Textfeld finden.
   * Robust: echtes Textfeld ist mal <textarea>, mal ein bearbeitbares div; das
   * Fenster hat nicht immer role="dialog". Erkennung daher textbasiert. */
  function findeModal() {
    // 1) Feld direkt über sein aria-label ("Öffentlich antworten").
    let feld =
      document.querySelector('textarea[aria-label*="ffentlich" i]') ||
      document.querySelector('[contenteditable="true"][aria-label*="ffentlich" i]') ||
      document.querySelector('[role="textbox"][aria-label*="ffentlich" i]');
    let modal = null;
    // 2) Über die Überschrift "Auf Rezension antworten".
    if (!feld) {
      modal = findeContainerMitText("auf rezension antworten");
      if (modal) feld = findeFeldIn(modal);
    }
    // 3) Irgendein Dialog mit bearbeitbarem Feld.
    if (!feld) {
      const dlg = document.querySelector('[role="dialog"]');
      if (dlg) feld = findeFeldIn(dlg);
      if (feld) modal = dlg;
    }
    if (!feld) return null;
    if (!modal) modal = feld.closest('[role="dialog"]') || findeContainerMitText("auf rezension antworten") || feld.parentElement || document.body;
    return { modal, feld };
  }

  function findeModalSubmit(modal) {
    const els = modal.querySelectorAll('button,[role="button"]');
    let treffer = null;
    for (const el of els) if (SUBMIT_WOERTER.includes(normText(el))) treffer = el;
    return treffer; // der (letzte) Senden/Antworten-Knopf im Fenster
  }

  // Bewertungstext grob aus dem Fenster lesen (Fallback, wenn kein Karten-Kontext).
  function leseModalReview(modal) {
    const ignor = [
      "auf rezension antworten",
      "öffentlich antworten",
      "inhaber",
      "antworten",
      "senden",
      "abbrechen",
      "mehr",
      "vollständige rezension ansehen",
      "der kunde wird über ihre antwort",
    ];
    let best = "";
    for (const roh of (modal.innerText || "").split("\n")) {
      const l = roh.trim();
      if (!l || /^\d+\/\d+$/.test(l)) continue;
      const low = l.toLowerCase();
      if (ignor.some((i) => low.includes(i))) continue;
      if (l.length > best.length) best = l;
    }
    return best;
  }

  /* Kudora in Googles Antwort-Fenster einbauen: generieren, ins echte Textfeld
   * schreiben, "✓ Senden" (klickt Googles Senden-Knopf). Läuft egal ob das Fenster
   * über den Kudora-Knopf ODER über Googles "Antworten" geöffnet wurde. */
  async function behandleModal() {
    const gefunden = findeModal();
    if (!gefunden) return;
    const { modal, feld } = gefunden;
    if (feld.dataset.kudoraModal) return; // schon eingebaut
    feld.dataset.kudoraModal = "1";

    const leiste = document.createElement("div");
    leiste.className = "kudora-bar kudora-modal-bar";
    const gen = document.createElement("button");
    gen.type = "button";
    gen.className = "kudora-btn";
    gen.textContent = "✨ Mit Kudora schreiben";
    const senden = document.createElement("button");
    senden.type = "button";
    senden.className = "kudora-senden";
    senden.textContent = "✓ Senden";
    senden.style.display = "none";
    leiste.appendChild(gen);
    leiste.appendChild(senden);
    // Schön platzieren: direkt vor Googles eigenem "Antworten"-Knopf (unten
    // rechts, neben dem Hinweistext). Sonst gleich unter das Textfeld.
    const submitJetzt = findeModalSubmit(modal);
    if (submitJetzt) submitJetzt.insertAdjacentElement("beforebegin", leiste);
    else feld.insertAdjacentElement("afterend", leiste);

    const ctx = { original: "", sterne: 5, entwurf: "" };

    async function generiere() {
      const quelle = modalKontext || {
        original: leseModalReview(modal),
        sterne: 5,
      };
      ctx.original = quelle.original;
      ctx.sterne = quelle.sterne || 5;
      if (!ctx.original) {
        gen.textContent = "⚠ Keine Bewertung erkannt";
        return;
      }
      gen.disabled = true;
      gen.textContent = "✨ Kudora schreibt …";
      const res = await holeAntwort({
        original: ctx.original,
        sterne: ctx.sterne,
        betrieb: "",
      });
      gen.disabled = false;
      if (!res || res.ok === false) {
        gen.textContent = "⚠ Nochmal versuchen";
        gen.title = (res && res.meldung) || "Fehler.";
        return;
      }
      ctx.entwurf = (res.entwurf || "").trim();
      setzeFeldwert(feld, ctx.entwurf);
      feld.focus();
      gen.textContent = "↻ Neue Formulierung";
      senden.style.display = "";
    }

    gen.addEventListener("click", () => {
      generiere().catch((e) => (gen.textContent = "⚠ " + String(e)));
    });
    senden.addEventListener("click", () => {
      const finale = feldWert(feld).trim();
      if (!finale) return;
      // Lernen (auch aus Änderungen), dann Googles Senden-Knopf klicken.
      sendeFreigabe({
        original: ctx.original,
        sterne: ctx.sterne,
        betrieb: "",
        entwurf: ctx.entwurf,
        finale_antwort: finale,
      });
      const submit = findeModalSubmit(modal);
      const aktiv =
        submit && !submit.disabled && submit.getAttribute("aria-disabled") !== "true";
      if (aktiv) {
        submit.click();
        senden.disabled = true;
        senden.textContent = "✓ Gesendet";
      } else {
        // Feld ist gefüllt, aber Googles Knopf reagiert (noch) nicht -> Nutzer klickt.
        senden.textContent = 'Jetzt „Antworten" klicken';
        senden.title =
          "Kudora hat die Antwort eingefügt und gelernt. Bitte klicken Sie Googles " +
          '"Antworten"-Knopf.';
      }
    });

    // Kamen wir über den Kudora-Knopf (Kontext gesetzt), sofort generieren.
    if (modalKontext) {
      await generiere();
      modalKontext = null;
    }
  }

  /* Klick auf den Kudora-Knopf einer Karte: Googles "Antworten" öffnen — das
   * Antwort-Fenster übernimmt dann (behandleModal). Gibt es (anderes Layout)
   * ein direktes Feld in der Karte, wird dieses gefüllt. */
  async function aufGenerieren(karte, btn) {
    try {
      const original = leseText(karte);
      if (!original) {
        knopfStatus(btn, "fehler", "Kein Bewertungstext gefunden.");
        return;
      }
      const sterne = leseSterne(karte);

      // Anderes Layout: direktes Antwortfeld in der Karte (nicht im Dialog).
      const feld = firstMatch(karte, S.reply);
      if (feld && !feld.closest('[role="dialog"]')) {
        knopfStatus(btn, "laden");
        const res = await holeAntwort({ original, sterne, betrieb: "" });
        if (!res || res.ok === false) {
          knopfStatus(btn, "fehler", (res && res.meldung) || "Fehler.");
          return;
        }
        const entwurf = (res.entwurf || "").trim();
        setzeFeldwert(feld, entwurf);
        feld.focus();
        const heikel =
          (res.risikowoerter && res.risikowoerter.length > 0) || sterne <= 3;
        if (heikel) zeigeHinweis(karte);
        else entferneHinweis(karte);
        knopfStatus(btn, "fertig");
        aktualisiereSendenKnopf(btn.parentNode, {
          karte,
          original,
          sterne,
          entwurf,
          feld,
          box: null,
        });
        return;
      }

      // Normalfall (Google Maps Inhaber): "Antworten" öffnen -> Modal übernimmt.
      modalKontext = { original, sterne };
      const trigger = findeTrigger(karte);
      if (trigger) {
        trigger.click();
        knopfStatus(btn, "standard"); // Karten-Knopf zurücksetzen
        return;
      }

      // Kein Weg zu antworten -> Inline-Box (kommt bei korrektem Gating kaum vor).
      knopfStatus(btn, "laden");
      const res = await holeAntwort({ original, sterne, betrieb: "" });
      if (!res || res.ok === false) {
        knopfStatus(btn, "fehler", (res && res.meldung) || "Fehler.");
        return;
      }
      zeigeInlineAntwort(btn.parentNode, (res.entwurf || "").trim());
      knopfStatus(btn, "standard");
    } catch (e) {
      knopfStatus(btn, "fehler", String(e));
    }
  }

  function injiziereKnopf(karte) {
    // Verschachtelte Karten: wenn ein Vorfahre schon einen Kudora-Knopf hat, raus.
    if (karte.parentElement && karte.parentElement.closest(".kudora-hat-knopf")) return;

    const schonBar = karte.querySelector(":scope > .kudora-bar");

    // Schon beantwortet -> evtl. vorhandenen Knopf entfernen, dann raus.
    if (istBeantwortet(karte)) {
      if (schonBar) schonBar.remove();
      karte.classList.remove("kudora-hat-knopf");
      return;
    }
    // Hier kann man nicht antworten -> kein Knopf.
    if (!kannAntworten(karte)) return;

    // Bar noch vorhanden -> nichts tun. Fehlt sie (Google hat beim Aufklappen
    // neu gerendert), bauen wir sie unten neu -> Knopf verschwindet nicht mehr.
    if (schonBar) return;

    karte.classList.add("kudora-hat-knopf");
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
      // Ist Googles Antwort-Fenster offen? Dann Kudora dort einbauen.
      behandleModal().catch(() => {});
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
