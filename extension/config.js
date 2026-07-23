/* Kudora-Konfiguration — DIESE ZWEI WERTE nach dem Deploy anpassen:
 *
 *   backendUrl : die öffentliche Adresse deines Servers (z. B. von Render),
 *                OHNE Schrägstrich am Ende. Lokal: http://localhost:8000
 *   token      : dasselbe Geheim-Token wie KUDORA_TOKEN auf dem Server.
 *                Lokal leer lassen ("").
 *
 * `self` funktioniert sowohl im Hintergrund (Service Worker) als auch im Popup.
 */
self.KUDORA_CONFIG = {
  backendUrl: "http://localhost:8000",
  token: "",
};
