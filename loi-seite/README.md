# LOI-Seite – CQ Property Management

Landingpage zum Einsammeln unverbindlicher Absichtserklärungen (LOIs) für die Haus- und SEV-Verwaltung.
Statische Seite (eine HTML-Datei plus `assets/`), kein Build-Schritt. Geplant unter `cashflowquartier.com/verwaltung/`.

## Inhalt
- Hero mit Teamfoto, Kennzahlen, Video (Google-Drive-Einbettung), OnePager-Download
- Leistungen: **Hausverwaltung** (Richtwert ca. 29 € brutto je Einheit/Monat) und **SEV-Verwaltung** (35–55 €)
- LOI-Formular in 5 Schritten: Leistung → Standorte → Zeitpunkt → Ausblick → Absender und Erklärung
- Abschluss mit Zusammenfassung zum Drucken/Speichern

## Lokal ansehen
```bash
cd loi-seite && python3 -m http.server 8765
```
Dann `http://localhost:8765/` öffnen.

## Personalisierte Links
```bash
python loi-seite/make_links.py empfaenger.csv --base https://cashflowquartier.com/verwaltung/ > links.csv
```
CSV-Spalten: `id, firma, anrede, name, position, email, typ`. Der Link enthält diese Angaben (Base64 im Parameter `r`):
Die Seite begrüßt den Empfänger mit Namen, füllt Schritt 5 vor und schickt die `id` als `ref_id` mit dem LOI mit.

## Anbindung an die Plattform (offen)
In `index.html` steht oben im Skript `const ENDPOINT = "";`. Leer bedeutet **Entwurfsmodus**: Es wird nichts gesendet.
Sobald die Plattform einen Endpunkt hat, kommt hier dessen URL hinein. Die Seite schickt dann je LOI ein JSON per `POST`:

```json
{
  "version": 1,
  "eingegangen": "2026-10-31T17:20:00.000Z",
  "ref_id": "fo-mustermann",
  "absender": { "firma": "…", "typ": "Family Office", "name": "…", "position": "…",
                "entscheider": "ja | mit | nein", "email": "…", "telefon": "… | null" },
  "leistungen": {
    "hausverwaltung": { "einheiten": 250, "objekte": 18, "preis_feedback": "passt | eher_hoch | zu_hoch | weiss_nicht", "richtwert_eur": 29 },
    "sev": { "einheiten": 60, "wegs": 25, "preis_feedback": "…", "richtwert_eur": "35-55" }
  },
  "standorte": [ { "plz": "42103", "ort": "Wuppertal", "einheiten": 200, "leistung": "hv | sev", "nutzung": "wohnen | gewerbe | gemischt" } ],
  "zeitpunkt": { "start": "sofort | 2027-Q2 | spaeter | offen", "verwaltung_heute": "eigen | extern | gemischt",
                 "kuendbar_ab": "12/2026", "kosten_heute": "32 € brutto" },
  "ausblick": { "zusatzleistungen": ["energie", "versicherung", "gutachten", "mieterhoehung", "vertrieb"],
                "zukaeufe_24m": 100, "pilot": "ja | vielleicht | nein", "wahrscheinlichkeit": 4, "anmerkungen": "…" },
  "nennung_investoren": "namentlich | anonym | nein",
  "erklaerungen": { "unverbindlich": true, "datenschutz": true }
}
```
`leistungen.hausverwaltung` bzw. `leistungen.sev` ist `null`, wenn die Leistung nicht gewählt wurde.

Der Endpunkt sollte:
1. daraus ein **Projekt in der Pipeline „LOI Verwaltung“** in CashFlow Quartier anlegen (Titel: Firma + Einheiten gesamt),
2. die **Bestätigungs-Mail mit PDF** an den Absender schicken, unterschrieben von Jan-Moritz Becker,
3. eine Kopie an kontakt@cashflowquartier.com senden,
4. CORS für `https://cashflowquartier.com` erlauben und Spam abwehren (z. B. Cloudflare Turnstile).

## Vor dem Livegang prüfen
- Unverbindlichkeits- und Datenschutztext kurz anwaltlich prüfen lassen
- Links zu Impressum und Datenschutz (`cashflowquartier.com/impressum`, `/datenschutz`) prüfen
- Drive-Video für „Jeder mit dem Link“ freigeben, sonst bleibt die Einbettung leer
- Leistungstexte in den beiden Karten gegenlesen
