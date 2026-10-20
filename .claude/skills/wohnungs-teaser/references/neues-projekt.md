# Neues Projekt anlegen

Gilt, wenn es für den genannten Drive-Ordner noch keine `projects/<slug>/facts.yaml` gibt. Vorlage:
`projects/freiligrathstr-oberhausen/facts.yaml` (kopieren, Inhalte ersetzen). `<slug>` = kurz, z. B. `musterstr-duisburg`.

## 1. Ordnerstruktur erkunden
Unterordner per `search_files` (`parentId = '<id>'`) auflisten. Typisch:
`intern/` (PE-Excel, Exposé, ValuePaper), `Projektübersicht/` mit `Bilder/WE/Haus …/<Lage>`, `Bilder/Allgem.`, `MV/` (Mieterliste),
`E-Ausweis/`, `Pläne:Wohnfläche/`, `TE/` (Teilungserklärung), Baubeschreibung. Projektordner-ID in `drive.projektordner_id`.

## 2. Fakten sammeln (Subagent, parallel zu 3 und 4)
Prompt-Kern: „Lies per `read_file_content` Exposé, Baubeschreibung, Energieausweise, Mieterliste, Besichtigungsnotizen und
Wohnflächenaufstellung und liefere ein deutsches Faktenblatt: Adressen inkl. PLZ, Baujahr, Anzahl Häuser/Wohnungen, Bauweise,
Heizung, Keller/Außenflächen, Energieausweis je Haus (Art, kWh/(m²·a), Klasse, Energieträger), Lage laut Exposé, geplante Maßnahmen.
Nur belegte Angaben, Zahlen wörtlich, nichts erfinden; fehlende Angaben als ‚nicht gefunden‘.“
→ `objekt`, `haeuser` in facts.yaml füllen.

## 3. Teilungserklärung abgleichen (Subagent)
TE lesen (`read_file_content`, sonst PDF herunterladen und `pdftotext`/Seiten als Bild). Tabelle Nr. | Haus | Geschoss | Lage | MEA
erstellen und mit `python -m teaser_generator.cli --pe <xlsx> --list` (Spalte „Einheit“) vergleichen. Abweichungen (vertauschte
Seiten, zusammengelegte Einheiten, Flächen ≠ MEA-Verhältnis) in `drive.hinweise_te` + dem Nutzer melden.

## 4. Lage-Recherche (Subagent mit WebSearch/WebFetch)
Für Stadt und Stadtteil, jeweils mit Quelle und Jahr:
- Einwohner + Entwicklung (IT.NRW bzw. Landesstatistik, Stadt), Stadtteil-Einwohner
- Anbindung: Autobahnen/Anschlussstellen, Bahnhof/ÖPNV, Fahrzeiten zu Großstädten, Flughafen
- Große Arbeitgeber mit Beschäftigten, sozialversicherungspflichtig Beschäftigte am Arbeitsort, Region
- Leuchtturm-Investitionen/Freizeitmagnete mit Besucherzahlen, Städtebauförderung, neue Quartiere
- Grün/Nahversorgung im Stadtteil
- Angebotspreise Eigentumswohnungen (€/m²) und Angebotsmieten (€/m²) für Stadtteil/Adresse aus mehreren Portalen
  (Immowelt, ImmoScout24, Engel & Völkers, Immoportal, miet-check, LL u. a.)
Direkte Abrufe sind in dieser Umgebung oft gesperrt → Websuche-Auszüge nutzen; Seiten mit Playwright im Higgsfield-Sandbox
(`sandbox_exec`, `NODE_PATH=$(npm root -g) node script.js`) abrufen, wenn nötig.
**Homeday-Preisatlas immer** für die konkrete Adresse abfragen (im Sandbox per Playwright):
`https://www.homeday.de/de/preisatlas/<stadt>/<straße>+<nr>,+<plz>?map_layer=standard&marketing_type=sell&property_type=apartment`
(und `marketing_type=rent`); Wert „Ø … €/m²“ aus dem Seitentext.
Ergebnis in `lage` (titel, intro, 4 kennzahlen, 4–6 abschnitte mit punkten, preise mit quellen-Listen, quellen-Fußnote).
**Negative Kennzahlen weglassen** (siehe regeln.md).

## 5. Mietrecht
Mieterschutzverordnung des Bundeslandes prüfen (Gemeindeliste: abgesenkte Kappungsgrenze 15 %, Mietpreisbremse).
→ `mietrecht: {kappungsgrenze: 0.20 oder 0.15, mietpreisbremse: true/false, hinweis: "…mit Quelle…"}`.

## 6. Drive-Ordner je Einheit
Im Projektordner je TE-Nummer `WE <Nr> – <Adresse laut PE-Excel>` mit `Ist-Bilder`/`Soll-Bilder` anlegen (Subagent, vorher auf
Bestehendes prüfen, nichts doppelt anlegen). IDs in `drive.einheiten` eintragen. Zusammengelegte Einheiten: ein Ordner
(„WE 17 – … (inkl. WE 18 …)“).

## 7. Upload-Briefkasten
Falls `tools/drive_upload.gs` genutzt wird: Projektordner-ID in `ERLAUBTE_WURZELN` des Apps Scripts ergänzen lassen (Nutzer).
