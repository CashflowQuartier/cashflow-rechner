# cashflow-rechner – Wohnungs-Teaser-Generator

Erzeugt aus der PE-Excel eines Projekts und den Unterlagen im Drive-Projektordner einen Verkaufs-Teaser
(PDF, A4) pro WEG-Wohnung.

Der Teaser enthält:
- Titelseite mit Kennzahlen: Kaufpreis = Gesamtinvest, Miete ab Tag 1, Rendite, monatliches Ergebnis
- Konzeptseite: Mietsubvention, Renovierungsrückstellung, WEG-Sanierung, übernommene Kaufnebenkosten, dazu Lage und Objektdaten
- Wohnung heute: Fotos, Wohnungsdaten, Zusammensetzung des Kaufpreises
- Subventionsstaffel bis zur SOLL-Miete (Diagramm und Tabelle) sowie die Rückstellungen
- Visualisierung nach Renovierung, wenn die Reno-Rückstellung SE über 5.000 € liegt
- Cashflow-Rechnung: Monat 1 und 10-Jahres-Vorschau mit Zins, Tilgung, AfA, Steuer, HV/MV und Rücklagen

## Nutzung
```bash
pip install -r requirements.txt
python -m teaser_generator.cli --pe "PE - ….xlsx" --list
python -m teaser_generator.cli --pe "PE - ….xlsx" --facts projects/<slug>/facts.yaml --unit 33 \
  --cover aussen.jpg --photos wohnen.jpg kueche.jpg bad.jpg \
  --renders reno_wohnen.jpg reno_kueche.jpg reno_bad.jpg --out out/Teaser_WE33.pdf
```
Für die PDF-Erzeugung wird Headless-Chromium verwendet (`CHROMIUM_PATH` setzen, falls nicht automatisch gefunden).

Projekt-Teaser über alle Einheiten (allgemeine Infos, Beispielrechnung, Preisliste; `--whitelabel` ohne CFQ-Branding):
```bash
python -m teaser_generator.cli --pe "PE - ….xlsx" --facts projects/<slug>/facts.yaml --projekt --unit 1 \
  --cover aussen.jpg --galerie a.jpg b.jpg c.jpg --out out/Teaser_Projekt.pdf
```

## Mit Claude (Skill „wohnungs-teaser“)
In einer neuen Claude-Code-Sitzung mit diesem Repo genügt: „Teaser für <Projektordner>, WE <Nr>“.
Ablauf, Regeln und Recherche-Anleitung: `.claude/skills/wohnungs-teaser/` (SKILL.md + references/).
Hilfsskripte: `tools/drive_decode.py` (Drive-Downloads entpacken), `tools/contact_sheet.py` (Foto-Übersicht),
`teaser_generator/drive_upload.py` + `tools/DRIVE_UPLOAD.md` (Upload in Drive).

## Aufbau
- `teaser_generator/pe_excel.py`: liest die PE-Excel, Spalten werden über ihre Überschriften gefunden
- `teaser_generator/finance.py`: Subventionsstaffel und Cashflow (identisch mit den Excel-Formeln)
- `teaser_generator/templates/teaser.html`: Layout
- `projects/<slug>/facts.yaml`: Objektfakten je Projekt (Lage, Baujahr, Energie …)

Fotos, Excel und PDFs gehören nicht ins Repo (`.gitignore`), weil sie personenbezogene Mieterdaten enthalten.
