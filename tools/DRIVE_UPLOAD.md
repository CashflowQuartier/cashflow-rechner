# Upload-Briefkasten: Teaser-PDFs und Soll-Bilder direkt in Google Drive

Der Drive-Connector kann keine größeren Dateien hochladen. Deshalb legt ein kleines Google-Apps-Script
(„Upload-Briefkasten“) die Dateien im Namen deines Google-Kontos in den WE-Ordnern ab.

## 1. Script anlegen (einmalig, ca. 5 Minuten, am besten am Computer)
1. https://script.google.com öffnen (mit dem Google-Konto, das Zugriff auf die geteilte Ablage hat) → **Neues Projekt**.
2. Den Inhalt von `tools/drive_upload.gs` komplett in den Editor kopieren (vorhandenen Code ersetzen).
3. In der Zeile `const TOKEN = '…'` eine eigene, lange Zufallszeichenfolge eintragen (z. B. 40 Zeichen aus einem Passwortgenerator).
4. Bei `ERLAUBTE_WURZELN` stehen die Projektordner, in die abgelegt werden darf. Für neue Projekte deren Ordner-ID ergänzen.
5. Speichern → **Bereitstellen → Neue Bereitstellung** → Typ **Web-App**:
   - Ausführen als: **Ich**
   - Zugriff: **Jeder**
6. Zugriff erlauben (Google fragt nach Drive-Berechtigung) → die angezeigte **Web-App-URL** kopieren.

## 2. In der Claude-Umgebung hinterlegen (einmalig)
Umgebungsmenü in der Titelleiste der Sitzung → **Bearbeiten**:
- **Umgebungsvariablen / Network secrets:**
  - `CFQ_DRIVE_UPLOAD_URL` = die Web-App-URL
  - `CFQ_DRIVE_UPLOAD_TOKEN` = das Token aus Schritt 1.3
- **Netzwerkzugriff → Allowed domains:** `script.google.com` und `script.googleusercontent.com` ergänzen
  (Haken „Allow package managers“ gesetzt lassen). Empfohlen zusätzlich: `upload.higgsfield.ai` und
  `d8j0ntlcm91z4.cloudfront.net`, dann können die echten Wohnungsfotos für die Visualisierung genutzt werden.

Neue Sitzungen übernehmen die Einstellungen automatisch.

## Sicherheit
- Ohne das Token nimmt das Script nichts an; es legt nur in den freigegebenen Projektordnern ab.
- Token nie in den Chat oder ins Repo schreiben. Bei Verdacht: neues Token eintragen und neu bereitstellen.
- Gleichnamige Dateien im Zielordner werden ersetzt (alte Version landet im Papierkorb).
