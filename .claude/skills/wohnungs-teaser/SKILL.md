---
name: wohnungs-teaser
description: Erstellt Verkaufs-Teaser (7-seitiges PDF im Cashflow-Quartier-Design) für einzelne WEG-Wohnungen aus einem Google-Drive-Projektordner – inklusive Renovierungs-Visualisierungen, Cashflow- und Steuerrechnung, Lage-Recherche und Ablage im Drive. Verwenden, sobald der Nutzer einen Projektordner („PE - …“) und eine oder mehrere Wohnungen (WE-Nummer) nennt und einen Teaser, ein Exposé oder Verkaufsunterlagen möchte – z. B. „Teaser für PE - IR - Freiligrathstrasse, WE 3“.
---

# Wohnungs-Teaser

**Eingabe des Nutzers:** Projektordner (Name im Drive, z. B. „PE - IR - Freiligrathstrasse 8-10, Oberhausen“) + Wohnung(en) als
**WE-Nummer laut Teilungserklärung**. Mehr braucht es nicht – alles andere holt sich dieser Skill selbst.

**Ergebnis je Wohnung:** `out/<slug>/Teaser_WE<NN>_<Straße><Nr>_<Lage>.pdf` (7 Seiten), Ist-Fotos im Drive-Ordner
`WE <Nr> – …/Ist-Bilder`, Soll-Bilder + PDF hochgeladen bzw. im Chat ausgeliefert.

Freigaben des Nutzers (Stand 10/2026): Higgsfield-Bildgenerierung generell erlaubt – nicht nachfragen.
Ansprache im Teaser immer „du“. Mit dem Nutzer auf Deutsch kommunizieren.

Weitere Dateien dieses Skills – bei Bedarf lesen:
- `references/regeln.md` – verbindliche Produkt-, Darstellungs- und Zuordnungsregeln (**vor dem ersten Teaser einer Sitzung lesen**)
- `references/neues-projekt.md` – Projekt zum ersten Mal: facts.yaml anlegen, Lage- und Mietrecht-Recherche
- `references/bilder.md` – Fotos auswählen, Visualisierungen erzeugen und herunterladen (Higgsfield)

Code: `teaser_generator/` (Generator), `tools/` (Hilfsskripte), Firmen-Konfiguration `teaser_generator/config/cfq.yaml`,
Projekte `projects/<slug>/facts.yaml`. Arbeitsdateien (Excel, Fotos, Renders) nur im Scratchpad, **nie ins Repo**
(personenbezogene Mieterdaten). Unten steht `$S` für das Scratchpad-Verzeichnis der Sitzung.

## Ablauf (Checkliste)

### 1. Projekt erkennen
- Gibt es `projects/<slug>/facts.yaml` mit `drive.ordner` = genannter Ordner? → **bekanntes Projekt** (Schritt 2 überspringen
  bis auf PE-Excel laden). Sonst → **neues Projekt**: zuerst `references/neues-projekt.md` abarbeiten.
- Drive-Ordner suchen: `search_files` mit `title contains '<Teil des Namens>' and mimeType = 'application/vnd.google-apps.folder'`.

### 2. PE-Excel laden und Einheit prüfen
- Neueste Datei „… PE …xlsx“ im Projektordner (meist `intern/`) per `download_file_content` laden, dann
  `python tools/drive_decode.py $S/drive <file-id>` → `$S/drive/<id>.xlsx`.
- `python -m teaser_generator.cli --pe <xlsx> --list` → Zeile `WE <Nr> (PE <interne Nr>)` der gewünschten Wohnung.
  **WE-Nr. = Spalte „Einheit“ = Nummer laut Teilungserklärung.** Status (vermietet/frei), Fläche, Reno-Rückstellung notieren.
- `drive.hinweise_te` in facts.yaml beachten (bekannte Abweichungen zwischen TE und Excel). Betrifft eine Abweichung die Wohnung
  → **erst beim Nutzer nachfragen**, keinen Teaser erstellen.

### 3. Fotos
- Ordner `Projektübersicht/Bilder/WE/Haus Nr. <X>/<Lage>` suchen; Zuordnung nur über Haus + Geschoss + Lage (+ Fläche),
  nie über Nummern in Ordnernamen. Fehlt ein Fotoordner oder ist die Zuordnung unklar → Nutzer fragen.
- Alle Fotos laden → `python tools/drive_decode.py $S/units/we<Nr> <ids…>` → `python tools/contact_sheet.py $S/units/we<Nr> $S/we<Nr>_sheet.jpg`
  → Kontaktabzug ansehen und 2–3 Fotos wählen (Reihenfolge: Wohnen, Küche, Bad; sonst Schlafzimmer). **Keine Fotos mit Personen.**
- Titelbild = Außenansicht des Hauses aus `Bilder/Allgem.`; für bekannte Projekte steht die Drive-ID in `facts.yaml → drive.titelbild_id`.

### 4. Visualisierungen (nur wenn Reno-Rückstellung SE > 5.000 €)
Je gewähltem Ist-Foto ein passendes Soll-Bild – Details, Prompt-Vorlage und Download-Weg in `references/bilder.md`.

### 5. PDF bauen und prüfen
```
python -m teaser_generator.cli --pe <xlsx> --facts projects/<slug>/facts.yaml --unit <WE-Nr> \
  --cover <aussen.jpg> --photos <ist1> <ist2> <ist3> --renders <soll1> <soll2> <soll3> \
  --out out/<slug>/Teaser_WE<NN>_<Straße><Nr>_<Lage>.pdf
```
- `--photos` und `--renders` in derselben Reihenfolge (Paare). Warnungen des Generators (z. B. Kappungsgrenze) an den Nutzer weitergeben.
- **Jede Seite ansehen**: `pdftoppm -r 50 -png <pdf> $S/prev` und als Raster prüfen – nichts darf in die Fußzeile ragen,
  keine abgeschnittenen Köpfe/Tabellen, Titel einzeilig. Bei Problemen Template anpassen, nicht die Zahlen.

### 6. Ablage im Drive
- WE-Ordner `WE <Nr> – <Adresse>` im Projektordner (IDs in `facts.yaml → drive.einheiten`, sonst per `search_files`
  `title contains 'WE <Nr> '` suchen; fehlt er: Ordner + Unterordner `Ist-Bilder`, `Soll-Bilder` anlegen).
- Ist-Fotos: `copy_file` in `Ist-Bilder`, Titel `WE<NN>_Ist_<Raum>.jpeg`.
- Soll-Bilder + PDF: wenn `CFQ_DRIVE_UPLOAD_URL`/`CFQ_DRIVE_UPLOAD_TOKEN` gesetzt sind:
  `python -m teaser_generator.drive_upload <soll-id> <soll-bilder…>` und `… <we-ordner-id> <pdf>`.
  Sonst: per `SendUserFile` ausliefern und Zielordner nennen (Einrichtung des Uploads: `tools/DRIVE_UPLOAD.md`).
- Neue Ordner-IDs in `facts.yaml → drive.einheiten` nachtragen.

### 7. Abschluss
- Code-/Konfigurationsänderungen committen und pushen (Arbeitsdateien bleiben im Scratchpad).
- Dem Nutzer kurz melden: verwendete PE-Datei, gewählte Fotos, Besonderheiten (leer stehend, fehlende Fotos/Daten,
  Abweichungen TE ↔ Excel, Generator-Warnungen), Ablageort. Visualisierungen sind KI-Beispielbilder (im PDF gekennzeichnet).

## Variante: Projekt-Teaser (ein PDF für alle Einheiten)
Wenn der Nutzer einen Teaser „für alle Einheiten“ bzw. das ganze Projekt will: allgemeine Infos + Beispielrechnung einer Wohnung + Preisliste.
```
python -m teaser_generator.cli --pe <pe.xlsx> --facts projects/<slug>/facts.yaml --projekt --unit <Beispiel-WE> \
  --cover <aussen.jpg> --galerie <bild1> <bild2> <bild3> --out out/<slug>/Teaser_<Projekt>.pdf
```
Seiten: Cover · Projekt (Galerie, Häuserübersicht, Objektdaten) · Sanierung & Energie · Beispielrechnung · Konzept/Subvention ·
Preisliste (hausweise, automatisch auf Seiten verteilt) · Lage · Zusammenfassung · Team. Projekttexte stehen in `facts.yaml → projekt`
(Vorlage: `projects/tannenbergstr-eschweiler/facts.yaml`).
`--whitelabel` erzeugt dieselbe Mappe ohne Logo, Kontaktdaten, Team-Seite, CFQ-Kennzahlen/Zitate und in neutralen Farben
(Dateiname mit `_WhiteLabel`). Danach per `pdftotext … | grep -i cashflow` prüfen, dass kein Branding übrig ist.
Die Seiten 3–7 des Wohnungs-Teasers liegen als `templates/_seite_*.html` (+ `_style.css`) und gelten für beide Teaser.
