# Prompt: Vertriebsassistenz darf Änderungsanträge im Verkaufsboard prüfen und freigeben

> Diesen Text komplett in eine Claude-Code-Sitzung im **Repository der CashFlow-Quartier-Plattform** (app.cashflowquartier.com) einfügen.

---

## Ausgangslage

Im Verkaufsboard (Verkaufsprojekte) können Vertriebler **Änderungsanträge** stellen (Feld, alter Wert, neuer Wert, Begründung). Heute kann nur Jan-Moritz Becker (Inhaber/Vertriebsleitung) diese Anträge freigeben oder ablehnen, und nur er wird bei neuen Anträgen benachrichtigt.

**Michelle Karthaus** (michellekarthaus@cashflowquartier.com) ist die Vertriebsassistenz. Sie soll Änderungsanträge genauso wie Jan-Moritz **prüfen, kommentieren, freigeben und ablehnen** können, und sie soll **bei jedem neuen Antrag benachrichtigt** werden.

## Was umgesetzt werden soll

1. **Berechtigung zum Entscheiden**
   - Finde heraus, wie die Berechtigung für das Entscheiden über Änderungsanträge im Verkaufsboard heute geprüft wird (Rolle, Permission-Flag, harte Prüfung auf Inhaber o. Ä.). Prüfe dabei Backend/API **und** Frontend (Buttons „Freigeben“/„Ablehnen“) sowie die MCP-Werkzeuge `decide_sale_change_request`, `list_sale_change_requests` und `add_sale_change_request_message`.
   - Führe eine **eigene, zuweisbare Berechtigung** ein (z. B. `sales.change_requests.decide`), statt Michelle die volle Inhaber-/Vertriebsleitungsrolle zu geben. Sie soll **nicht** automatisch weitere Rechte bekommen (z. B. Projektkalkulation, Löschen, Käufer festlegen).
   - Bestehende Inhaber/Vertriebsleitung behalten das Recht unverändert.
   - Weise die neue Berechtigung Michelle Karthaus zu. Falls Rechte über eine Rolle laufen, lege eine Rolle „Vertriebsassistenz“ an oder erweitere sie, statt Code mit festen Nutzer-IDs zu bauen.
   - Freigaben und Ablehnungen durch Michelle müssen wie bisher im Verlauf des Verkaufsprojekts stehen, mit **ihrem Namen** als Entscheiderin.

2. **Benachrichtigung bei neuen Änderungsanträgen**
   - Finde heraus, wie Jan-Moritz heute bei einem neuen Antrag informiert wird (In-App-Benachrichtigung, E-Mail, Push).
   - Stelle die Empfängerlogik so um, dass **alle Nutzer mit der Entscheidungsberechtigung** auf denselben Kanälen benachrichtigt werden, also auch Michelle. Keine fest eingetragenen Empfänger.
   - Auch Folgeereignisse (neue Nachricht im Antrag, Antrag entschieden) sollen an alle Entscheider gehen, sofern Jan-Moritz diese heute bekommt.
   - Wer selbst entschieden oder geschrieben hat, bekommt dazu keine eigene Benachrichtigung.

3. **Übersicht offener Anträge (falls noch nicht vorhanden)**
   - Für Entscheider soll es eine Ansicht bzw. einen Filter „Offene Änderungsanträge“ über **alle** Verkaufsprojekte geben, mit: Objekt/Adresse, Einheit, Vertriebler, Feld, alter → neuer Wert, Begründung, Datum, Link zum Projekt.
   - Gibt es so eine Ansicht schon, nur sicherstellen, dass Michelle sie sieht.

## Vorgehen

- Erst den bestehenden Code lesen und mir kurz zusammenfassen, wie Rechte und Benachrichtigungen heute funktionieren und was du ändern willst. **Danach** umsetzen.
- Datenbankänderungen nur über Migrationen.
- Tests ergänzen: (a) Michelle darf entscheiden, (b) ein normaler Vertriebler darf es weiterhin nicht, (c) ein neuer Antrag benachrichtigt Jan-Moritz **und** Michelle.
- Arbeite auf einem eigenen Branch, committe und pushe dorthin. Kein Merge in den Hauptzweig ohne meine Freigabe.
- Am Ende: kurze Zusammenfassung, was geändert wurde, wie ich es prüfen kann und ob noch ein Schritt in der Admin-Oberfläche nötig ist (z. B. Rolle zuweisen).

## Akzeptanzkriterien

- [ ] Michelle sieht bei offenen Änderungsanträgen die Buttons „Freigeben“ und „Ablehnen“ und kann sie nutzen.
- [ ] Michelle kann im Antrag Nachrichten schreiben.
- [ ] Michelle bekommt bei jedem neuen Änderungsantrag dieselbe Benachrichtigung wie Jan-Moritz.
- [ ] Vertriebler ohne die neue Berechtigung können weiterhin nicht entscheiden.
- [ ] Michelle hat keine zusätzlichen Rechte außer den oben genannten.
- [ ] Entscheidungen sind im Verlauf mit dem Namen der entscheidenden Person sichtbar.
