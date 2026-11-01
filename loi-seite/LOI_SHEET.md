# LOIs in ein Google Sheet schreiben (einmalig, ca. 5 Minuten)

Jedes abgeschickte LOI landet als Zeile in einem Google Sheet, der Absender bekommt automatisch eine
Bestätigung mit PDF in deinem Namen, und kontakt@cashflowquartier.com bekommt eine Kopie.
Das Sheet lässt sich jederzeit als Excel herunterladen (Datei → Herunterladen → Microsoft Excel).

1. In Google Drive ein neues Google Sheet anlegen, z. B. „CQPM – LOIs Verwaltung“.
2. Im Sheet: **Erweiterungen → Apps Script**. Den vorhandenen Code löschen und den Inhalt von
   `loi-seite/loi_sheet.gs` komplett einfügen. Speichern.
3. Oben die Funktion **einrichten** auswählen und **Ausführen**. Google fragt nach Berechtigungen
   (Tabelle bearbeiten, E-Mails in deinem Namen senden) → zulassen. Danach gibt es die Blätter „LOIs“ und „Standorte“.
4. **Bereitstellen → Neue Bereitstellung** → Typ **Web-App**:
   - Ausführen als: **Ich**
   - Zugriff: **Jeder**
5. Die angezeigte **Web-App-URL** (endet auf `/exec`) kopieren und an Claude schicken.
   Sie wird in `index.html` bei `const ENDPOINT = "…"` eingetragen.

## Was im Sheet steht
- **LOIs:** eine Zeile je Absichtserklärung: Unternehmen, Ansprechpartner, Einheiten Hausverwaltung und SEV,
  Preis-Feedback, Standorte, frühester Start, heutige Verwaltung, Kündbarkeit, Zusatzleistungen, Zukäufe,
  Pilot, Wahrscheinlichkeit, Nennung gegenüber Investoren, Anmerkungen.
- **Standorte:** eine Zeile je Standort (PLZ, PLZ-Region, Ort, Einheiten, Leistung, Nutzung, Start).
  Damit lässt sich per Pivot-Tabelle auswerten, wie viele Einheiten in welcher Region ab wann infrage kommen.

## Hinweise
- Änderst du später den Code, musst du unter **Bereitstellen → Bereitstellungen verwalten** eine neue Version
  bereitstellen. Die URL bleibt gleich.
- Die Bestätigungsmail kommt von dem Google-Konto, das das Script bereitstellt. Am besten also mit deinem
  Konto janmoritzbecker@cashflowquartier.com einrichten. Abschalten: `BESTAETIGUNG_SENDEN = false`.
- Ein verstecktes Feld hält einfache Spam-Bots ab.
