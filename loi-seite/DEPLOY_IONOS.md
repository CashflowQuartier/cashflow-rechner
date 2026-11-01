# Livegang unter cashflowquartier.com/cqpm-loi

**Gewählter Weg:** Die Website cashflowquartier.com läuft auf **Onepage.io**, die Domain liegt bei IONOS.
Die LOI-Seite liegt deshalb auf dem IONOS-Webspace unter `cqpm-loi.cashflowquartier.com` und wird in Onepage
auf der Seite `cqpm-loi` bildschirmfüllend eingebettet (Code: `onepage_einbettung.html`).

1. IONOS Hosting → Webspace Explorer → Ordner `cqpm-loi` anlegen, `cqpm-loi.zip` hochladen und entpacken
   (im Ordner müssen `index.html` und `assets/` direkt liegen).
2. IONOS Domains & SSL → cashflowquartier.com → ⋮ → Subdomains verwalten → Subdomain `cqpm-loi` anlegen →
   ⋮ → Verwendungsart anpassen → Webspace → Ordner `/cqpm-loi`.
3. SSL-Zertifikat der Subdomain zuweisen, dann `https://cqpm-loi.cashflowquartier.com` testen.
4. Onepage: neue Seite mit URL `cqpm-loi`, Kopf- und Fußzeile ausblenden, HTML-/Embed-Block mit dem Code aus
   `onepage_einbettung.html` einfügen, veröffentlichen.
5. `https://cashflowquartier.com/cqpm-loi` testen (auch mit `?q=test`).

---

Allgemeine Varianten (falls sich das Hosting ändert):

Upload-Paket: `cqpm-loi.zip` (enthält direkt `index.html`, `cinematic.html` und `assets/`; im Ordner `cqpm-loi` entpacken).
Neu erzeugen: `python loi-seite/build_cinematic.py` und dann das ZIP wie in der Sitzung beschrieben packen.

## Schritt 1: Herausfinden, welches IONOS-Produkt die Website betreibt
1. Auf **login.ionos.de** einloggen.
2. Im Menü **Websites & Domains** öffnen.
3. Bei cashflowquartier.com nachsehen, was dort steht:
   - **Webhosting**, **WordPress** oder **Managed WordPress** → weiter mit **Weg A**
   - **MyWebsite**, **Website-Baukasten** oder **Website Builder** → weiter mit **Weg B**

## Weg A: Webhosting oder WordPress (Ergebnis: cashflowquartier.com/cqpm-loi)
1. In IONOS **Hosting** öffnen und beim Vertrag auf **Webspace** klicken (öffnet den „Webspace Explorer“, eine Dateiverwaltung im Browser).
2. Den Ordner suchen, in dem die Website liegt. Bei WordPress ist es der Ordner mit `wp-admin`, `wp-content` und `wp-config.php`.
   Welcher Ordner zur Domain gehört, steht unter **Domains → cashflowquartier.com → Zielverzeichnis**.
3. Dort `cqpm-loi.zip` hochladen und mit Rechtsklick **Entpacken**.
   Falls Entpacken nicht angeboten wird: ZIP am Computer entpacken und den Ordner `cqpm-loi` komplett hochladen
   (oder per SFTP, Zugangsdaten unter **Hosting → SFTP & SSH**, Programm z. B. FileZilla oder Cyberduck).
4. Ergebnis prüfen: Im Website-Ordner liegt jetzt `cqpm-loi/index.html` und `cqpm-loi/assets/…`.
5. **https://cashflowquartier.com/cqpm-loi/** aufrufen.

Hinweise:
- WordPress stört das nicht: Echte Ordner werden vor WordPress ausgeliefert.
- Die Cinematic-Version liegt unter `/cqpm-loi/cinematic.html`. Soll sie die Hauptseite sein, `index.html` und `cinematic.html` tauschen (umbenennen).
- Bei Änderungen nur die geänderte Datei (meist `index.html`) erneut hochladen und ersetzen.

## Weg B: Website-Baukasten (Ergebnis: cqpm-loi.cashflowquartier.com)
Im Baukasten lassen sich keine eigenen Seiten hochladen. Deshalb kommt die Seite zu einem kostenlosen Hoster, die Adresse bleibt eure Domain.
1. Auf **app.netlify.com/drop** gehen (kostenloses Konto anlegen) und den entpackten Ordner `cqpm-loi` ins Fenster ziehen.
   Netlify zeigt eine Adresse wie `xyz-123.netlify.app`.
2. In Netlify: **Domain management → Add a domain** → `cqpm-loi.cashflowquartier.com` eintragen.
3. In IONOS: **Domains → cashflowquartier.com → DNS → Eintrag hinzufügen**
   - Typ: **CNAME**
   - Hostname: **cqpm-loi**
   - Zeigt auf: die Netlify-Adresse aus Schritt 1 (z. B. `xyz-123.netlify.app`)
4. Nach einigen Minuten bis wenigen Stunden ist **https://cqpm-loi.cashflowquartier.com** erreichbar; Netlify richtet das SSL-Zertifikat automatisch ein.

## Danach (beide Wege)
1. **Google Sheet anbinden** (`LOI_SHEET.md`), Web-App-URL an Claude geben → neue `index.html` hochladen. Vorher läuft das Formular im Entwurfsmodus und speichert nichts.
2. **Test:** Formular einmal selbst ausfüllen → Zeile im Sheet, Bestätigungsmail mit PDF, Kopie an kontakt@.
3. **Datenschutzerklärung** auf cashflowquartier.com um Formular, Google Sheets/Mail und Video ergänzen.

## Video mit einem Klick
Liegt das Video als eigene Datei im selben Ordner, startet es mit einem Klick sofort und ohne Google.
1. Video verkleinern (720p, ca. 50–80 MB statt 232 MB):
   `ffmpeg -i CQPM_Video.mp4 -vf scale=-2:720 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 96k -movflags +faststart cqpm-video.mp4`
2. Datei nach `cqpm-loi/assets/` hochladen.
3. In `index.html` beim Player `data-mp4="assets/cqpm-video.mp4"` eintragen.
Alternative: Video bei Vimeo hochladen und die Vimeo-ID bei `data-vimeo="…"` eintragen.
