---
name: wohnungs-teaser
description: Erstellt Verkaufs-Teaser (PDF) für einzelne WEG-Wohnungen eines Cashflow-Quartier-Projekts aus dem Google-Drive-Projektordner. Verwenden, wenn der Nutzer einen Drive-Ordner / eine Immobilie nennt und Teaser, Exposé-Kurzfassung oder Verkaufsunterlagen für eine oder mehrere Wohnungen haben will.
---

# Wohnungs-Teaser aus dem Drive-Projektordner

Der Nutzer nennt einen Projektordner in der geteilten Ablage „Cashflow Quartier → Projektentwicklung“
(z. B. „PE - IR - Freiligrathstrasse 8-10, Oberhausen“) und optional einzelne Wohnungen.
Ergebnis: ein PDF pro Wohnung, erzeugt mit `python -m teaser_generator.cli`.

## Produktlogik (nicht verändern ohne Rücksprache)
- Produkt = nach WEG geteilte, meist vermietete Wohnung.
- **SOLL-Miete** = marktgerechte Miete (PE-Excel). Die Differenz Ist → SOLL wird per **Mietsubvention**
  bezahlt, und zwar so lange, wie gesetzliche Mieterhöhungen (Kappungsgrenze 20 % / 3 Jahre) brauchen.
- **Renovierungsrückstellung SE** pro Einheit: Budget für den Auszug des Bestandsmieters.
- **Sanierung WEG**: Rückstellung für Maßnahmen am Gemeinschaftseigentum (anteilig nach MEA). Falls vorhanden → in den Teaser.
- **Kaufnebenkosten übernimmt CFQ**: beurkundeter Kaufpreis = Gesamtinvest des Käufers.
- Alle Zahlen (Preise, Subvention, Rückstellungen, Cashflow-Parameter) kommen **ausschließlich aus der PE-Excel** („PE - …xlsx“).
  Die Formeln in `teaser_generator/finance.py` bilden die Excel exakt nach. Nach jeder Änderung prüfen, ob
  Brutto-CF, Steuer und Netto-CF weiterhin mit den Spalten AV/AX/AY übereinstimmen.

## Ablauf
1. **Ordner finden**: `mcp__Google_Drive__search_files` mit `title contains '<Name>' and mimeType = 'application/vnd.google-apps.folder'`,
   danach Unterordner per `parentId = '<id>'` auflisten. Typische Struktur:
   `intern/` (PE-Excel, Exposé, ValuePaper), `Projektübersicht/` (`Bilder/WE/Haus …/<Lage>`, `Bilder/Allgem.`, `MV/`, `E-Ausweis/`, `Pläne:Wohnfläche/`, `TE/`), Baubeschreibung.
   Gibt es mehrere PE-Dateien, die **neueste** „PE - …“ (Änderungsdatum) nehmen und dem Nutzer nennen.
2. **Dateien laden**: `mcp__Google_Drive__download_file_content` liefert JSON mit base64 in `content`. Große Antworten
   landen automatisch als Datei in `tool-results/`. Dekodieren: `jq -r .content <datei> | base64 -d > <ziel>`.
   Alles nach `$SCRATCH/<projekt>/` legen (Scratchpad), **nicht ins Repo** (Mieterfotos = personenbezogen).
3. **Einheiten prüfen**: `python -m teaser_generator.cli --pe <pe.xlsx> --list`.
4. **Fakten**: Gibt es `projects/<slug>/facts.yaml` noch nicht, wird sie aus Exposé, Baubeschreibung, Energieausweisen,
   Mieterliste und Besichtigungsnotizen erstellt. Das kann ein Subagent mit `read_file_content` übernehmen.
   Nur belegte Fakten verwenden, nichts erfinden. Vorlage: `projects/freiligrathstr-oberhausen/facts.yaml`.
5. **Fotos je Wohnung**: aus `Bilder/WE/Haus Nr. X/<Lage>` laden, bei Bedarf als Kontaktabzug ansehen und auswählen
   (Wohnzimmer zuerst, dann Küche und Bad). Titelbild: eine Außenansicht aus `Bilder/Allgem.`.
6. **Renovierungs-Visualisierungen**, wenn Reno-Rückstellung SE > 5.000 €: mit Higgsfield `generate_image_batch`
   (Modell `gpt_image_2_5`, quality high, 2k), je ein Bild für Wohnzimmer, Küche und Bad. Pflicht im Prompt:
   leer, neuer **brauner Vinylboden**, **weiße Wände**, **weiße Türen und Zargen**, **neue Schalter/Steckdosen**,
   **neuer Fliesenspiegel in der Küche**, **neues Bad**, einfacher Mietstandard, Altbau der 1960er.
   Ist-Fotos lassen sich aus dieser Umgebung nicht hochladen (upload.higgsfield.ai ist gesperrt). Deshalb nur
   Text-Prompts, die den Raum anhand der Ist-Fotos beschreiben (Fensterform, Raumform).
   Herunterladen geht ebenfalls nicht direkt (cloudfront gesperrt). Umweg: `sandbox_exec` lädt die Bilder per curl,
   verkleinert sie auf ≤ 1400 px (`convert … -quality 80`) und gibt sie über `image_paths` zurück (≤ 512 KiB gesamt).
   Die Rückgabe landet als `mcp-Higgsfield-blob-*.jpg` in `tool-results/`.
7. **PDF erzeugen**:
   ```
   python -m teaser_generator.cli --pe <pe.xlsx> --facts projects/<slug>/facts.yaml --unit <WE-Nr> \
     --cover <aussen.jpg> --photos <wohnen> <kueche> <bad> --renders <reno_wohnen> <reno_kueche> <reno_bad> \
     --out out/<slug>/Teaser_WE<nr>.pdf
   ```
   Danach mit `pdftoppm -r 80 -png` rendern und jede Seite ansehen (Überläufe, abgeschnittene Tabellen).
8. **Ausliefern**: PDF per `SendUserFile` schicken. Auf Wunsch per `mcp__Google_Drive__create_file` in den
   Ordner `folgt - Vertriebsordner` hochladen, aber nur nach Bestätigung durch den Nutzer.

## Dem Nutzer immer melden
- welche PE-Datei verwendet wurde,
- Wohnungen ohne Fotos, Mietvertrag oder Fakten (dort steht dann „–“),
- dass die Visualisierungen KI-Beispielbilder sind (im PDF gekennzeichnet).
