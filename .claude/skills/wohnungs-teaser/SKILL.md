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
6. **Renovierungs-Visualisierungen**, wenn Reno-Rückstellung SE > 5.000 €. Higgsfield ist vom Nutzer generell freigegeben
   (Stand 10/2026) – nicht mehr pro Wohnung nachfragen. Dann mit Higgsfield `generate_image_batch`
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

## Zuordnung & Ablage (verbindlich)
- **WE-Nummer = Nummer laut Teilungserklärung** (in der PE-Excel Spalte „Einheit“, 1…n), NICHT die Spalte „WE-Nr.“ der
  PE-Excel (interne Nummer, z. B. 33–60). Teaser, Ordner und Dateinamen verwenden immer die TE-Nummer.
- **WE-Nummern nie aus Ordnernamen übernehmen.** Maßgeblich sind PE-Excel und Teilungserklärung (Ordner `Projektübersicht/TE`).
  Vor dem ersten Teaser eines Projekts WE-Nr., Haus, Geschoss, Lage (li./re./mitte) und Fläche aus beiden abgleichen und
  Abweichungen dem Nutzer melden. Fotoordner (`Bilder/WE/Haus …/<Lage>`) nur über Haus + Geschoss + Lage + Fläche zuordnen;
  bei Widersprüchen (z. B. vertauschte Seiten) nachfragen statt raten.
- **Ablage im Drive:** Im Projektordner je Einheit ein Ordner `WE <TE-Nr> – <Adresse laut PE-Excel>` mit den Unterordnern
  `Ist-Bilder` und `Soll-Bilder`. Ist-Fotos per `copy_file` in `Ist-Bilder` kopieren. PDFs und erzeugte Soll-Bilder kann der
  Drive-Connector nur mit Base64-Inhalt hochladen (für Dateien dieser Größe nicht praktikabel) → per `SendUserFile` ausliefern
  und den Zielordner nennen.
- **Titelbild** ist immer eine Außenansicht des Hauses (aus `Bilder/Allgem.`), nie ein Wohnungsfoto.

## Darstellungsregeln (verbindlich)
- **Positiv darstellen:** Ist eine Markt- oder Standortkennzahl negativ (z. B. Bevölkerungsprognose, Beschäftigtenentwicklung,
  Preistrend), wird sie weggelassen und nicht erwähnt. Ausnahme: Die Zahlen der Käuferrechnung (Cashflow, Steuer, Bilanz) bleiben vollständig.
- **Marktvergleich Seite 4:** Angebotspreise und -mieten aus mehreren Quellen recherchieren, den **Homeday-Preisatlas für die
  konkrete Adresse** (`homeday.de/de/preisatlas/<stadt>/<straße+nr,+plz>?marketing_type=sell|rent&property_type=apartment`,
  per Playwright im Higgsfield-Sandbox, da direkt gesperrt) immer abfragen. Alle Quellen in `facts.yaml → lage.preise` eintragen; der Generator filtert:
  - Kauf: Quellen **unter** unserem Kaufpreis/m² (exkl. KNK) fliegen raus; gezeigt wird der Ø der übrigen. Bleibt keine übrig → Box aus.
  - Miete: Quellen mehr als 15 % unter der SOLL-Miete fliegen raus; gezeigt wird die Spanne (min–max). Box nur, wenn die SOLL-Miete in der Spanne liegt.
- **Mietrecht pro Projekt recherchieren:** Gilt in der Gemeinde eine abgesenkte Kappungsgrenze (z. B. 15 % statt 20 % in 3 Jahren)
  oder eine Mietpreisbremse (Mieterschutzverordnung des Bundeslandes, Anlage mit Gemeindeliste)? Ergebnis in `facts.yaml → mietrecht`
  eintragen. Der Generator warnt, wenn die PE-Excel mit einem anderen Erhöhungsfaktor rechnet – dann den Nutzer informieren.
- **SEV-Vertrag:** Subvention und Renovierungsrückstellung stehen laut Kaufvertrag dem Käufer zu und werden per SEV-Vertrag als zinsloses
  Darlehen an die Verwaltung gegeben. Renovierungen beauftragt CFQ und bezahlt sie aus der Rückstellung; die Rechnung lautet auf den
  Eigentümer, der sie steuerlich absetzen kann.

## Aufbau & Tonalität des Teasers
- Ansprache immer mit **„du“**, wie auf www.cashflowquartier.com. Design: Onest, Navy #050D2B, Gold #E9B33F.
- Titel: Straße · Wohnungsbezeichnung · Stadt (wird automatisch aus der Adresse in der PE-Excel gebildet).
- Seiten (7): 1 Cover · 2 Wohnung (Ist-/Soll-Bilder, Wohnungs- und Objektdaten, Kaufpreis) · 3 Cashflow, Steuerrechnung, Vermögensbilanz
  (10 Jahre, 3 % Wertsteigerung auf Kaufpreis exkl. KNK, Einsatz = Cashflow Monat 1 × 12 × 10) · 4 Lage · 5 Konzept, Subvention, SEV-Vertrag · 6 Konzept-Zusammenfassung (ohne EK finanzierbar, Marktmiete, keine Sondervermietung, Break-even-Miete, Portfolio-Aufbau) · 7 Team, Kundenstimmen, Links mit Icons.
- Firmenweite Angaben (Team, Links, Kundenstimmen, Portfolio-Beispiele, Kontakt) stehen in `teaser_generator/config/cfq.yaml`; projektbezogene in `projects/<slug>/facts.yaml`.
- Bilder werden im Generator exakt auf das Rahmenformat zugeschnitten und als `<img>` eingebettet – nie per CSS-Hintergrund (Apple Vorschau verzerrt sonst).
- Die Lage-Seite kommt aus `facts.yaml` → `lage`. Für jedes neue Projekt neu recherchieren: Bevölkerung, Anbindung, Arbeitgeber,
  Investitionen, Angebotspreise und -mieten, jeweils mit Quellen. Der Homeday-Preisatlas hat für kleinere Städte oft keine Wohnungsdaten.

## Dem Nutzer immer melden
- welche PE-Datei verwendet wurde,
- Wohnungen ohne Fotos, Mietvertrag oder Fakten (dort steht dann „–“),
- dass die Visualisierungen KI-Beispielbilder sind (im PDF gekennzeichnet).
