# Verbindliche Regeln für Wohnungs-Teaser

## Produktlogik (nicht ohne Rücksprache ändern)
- Produkt: nach WEG geteilte, meist vermietete Bestandswohnung als Kapitalanlage.
- **SOLL-Miete** = marktgerechte Miete laut PE-Excel. Die Differenz Ist → SOLL zahlt CFQ als **Mietsubvention**, so lange, wie
  gesetzliche Mieterhöhungen (Kappungsgrenze) brauchen, um die SOLL-Miete zu erreichen. Der Käufer bekommt ab Tag 1 die SOLL-Miete.
- **Renovierungsrückstellung SE**: Budget je Wohnung, um sie bei Auszug des Bestandsmieters (bzw. vor Neuvermietung, wenn leer)
  auf Marktmiet-Standard zu bringen.
- **Sanierung WEG**: Rückstellung für Maßnahmen am Gemeinschaftseigentum, anteilig nach MEA – immer im Teaser zeigen, wenn vorhanden.
  Zusätzliche Maßnahmen, die nicht in der Excel stehen (z. B. Umrüstung auf Wärmepumpe), in `facts.yaml → weg_zusatz`.
- **Kaufnebenkosten übernimmt CFQ**: beurkundeter Kaufpreis = Gesamtinvest; außer dem Gesamtinvest fallen keine Kosten an.
- **SEV-Vertrag**: Subvention und Renovierungsrückstellung stehen laut Kaufvertrag dem Käufer zu und werden per SEV-Vertrag als
  zinsloses Darlehen an die CFQ-Verwaltung gegeben. Die Verwaltung zahlt monatlich SOLL-Kaltmiete + NK-Vorauszahlung des Mieters aus.
  Renovierungen beauftragt CFQ und bezahlt sie aus der Rückstellung; die Rechnung lautet auf den Eigentümer (steuerlich absetzbar).
- **Alle Zahlen kommen aus der PE-Excel.** `teaser_generator/finance.py` bildet die Excel-Formeln exakt nach (Subvention Spalte O,
  Brutto-CF AV, Steuer AX, Netto-CF AY). Nach Änderungen am Rechenkern gegen die Excel prüfen.
- Cashflow-Bilanz (Seite 3): 3 % Wertsteigerung p. a. auf den Kaufpreis exkl. KNK (enthält die Renovierungsrückstellung),
  + Tilgung über 10 Jahre (Annuität), − Startschuld (Gesamtinvest) = Gewinn; Einsatz = Cashflow nach Steuern Monat 1 × 12 × 10.
- Steuerrechnung (Seite 3): Miete − Zins − AfA − pauschal 20 € Werbungskosten − nicht umlagefähiges Hausgeld (HV + MV + Sonstiges)
  = steuerliches Ergebnis; × Grenzsteuersatz (40 %) = Ersparnis.

## Zuordnung
- **WE-Nummer = Nummer laut Teilungserklärung** (PE-Excel Spalte „Einheit“). Die Excel-Spalte „WE-Nr.“ (z. B. 33–60) ist intern
  und erscheint nirgends. Teaser, Drive-Ordner und Dateinamen verwenden die TE-Nummer.
- WE-Nummern nie aus Ordnernamen ableiten. Vor dem ersten Teaser eines Projekts TE und Excel abgleichen
  (Haus, Geschoss, Lage, Fläche/MEA) und Abweichungen in `facts.yaml → drive.hinweise_te` festhalten + dem Nutzer melden.
- Fotoordner über Haus + Geschoss + Lage zuordnen; bei Widersprüchen nachfragen statt raten.

## Darstellung
- **Positiv darstellen:** Negative Markt- oder Standortkennzahlen (Bevölkerungsprognose, Beschäftigtenentwicklung, Preistrends)
  weglassen und nicht erwähnen. Die Zahlen der Käuferrechnung (Cashflow, Steuer, Bilanz) bleiben immer vollständig und unverändert.
- **Marktvergleich Seite 4:** alle recherchierten Quellen inkl. Homeday in `facts.yaml → lage.preise` eintragen; der Generator filtert:
  - Kauf: Quellen unter unserem Kaufpreis/m² (exkl. KNK) fliegen raus, gezeigt wird der Ø der übrigen; keine übrig → Box aus.
  - Miete: Quellen > 15 % unter der SOLL-Miete fliegen raus, gezeigt wird die Spanne; Box nur, wenn die SOLL-Miete darin liegt.
- **Mietrecht** je Projekt recherchieren (Kappungsgrenze 15/20 %, Mietpreisbremse) → `facts.yaml → mietrecht`. Warnt der Generator,
  dass die Excel einen anderen Erhöhungssatz nutzt, den Nutzer informieren.
- **Leere Wohnungen** (Status ≠ „Vermietet“): Texte sprechen automatisch von Neuvermietung. Dem Nutzer melden, dass die Excel-Zahlen
  (Subvention auf Basis der alten Miete) unverändert übernommen wurden.
- **Titelbild** immer Außenansicht des Hauses. Ist-Fotos ohne Personen. Visualisierungen als KI-Beispielbilder kennzeichnen (macht das Template).

## Design & Aufbau (im Template umgesetzt – nicht pro Teaser ändern)
- Design nach www.cashflowquartier.com: Schrift Onest, Navy #050D2B, Gold #E9B33F, Grauflächen, große Radien, Gold-Unterstreichung.
- Titel: „Straße · Wohnung <Lage> · Stadt“ (automatisch aus der Adresse).
- 7 Seiten: 1 Cover (Kennzahlen, 3 Häkchen: Gemeinschaftseigentum, Renovierungsrückstellung, KNK) · 2 Wohnung (Ist/Soll-Bilder,
  Wohnungs-/Objektdaten, Kaufpreis) · 3 Cashflow, Steuerrechnung, Vermögensbilanz · 4 Lage · 5 Konzept, Subventionsstaffel, SEV ·
  6 Konzept-Zusammenfassung + Portfolio · 7 Team (2×5 quadratische Fotos), Kundenstimmen, Links mit Icons.
- Firmenweite Angaben (Team inkl. Nachnamen und Beschreibungen, Links, Kundenstimmen, Kennzahlen, Kontakt) in
  `teaser_generator/config/cfq.yaml` pflegen – nicht im Template.
- Bilder werden im Generator exakt auf das Rahmenformat zugeschnitten und als `<img>` eingebettet (sonst verzerrt Apple Vorschau).
