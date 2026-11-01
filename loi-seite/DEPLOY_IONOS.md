# Livegang auf IONOS unter cashflowquartier.com/cqpm-loi

Welcher Weg passt, hängt davon ab, welches IONOS-Produkt die Website betreibt.
Im IONOS-Kundenkonto unter **Menü → Websites & Domains** sieht man es:

## A) Webhosting oder WordPress bei IONOS (Dateizugriff per SFTP vorhanden)
Dann geht `cashflowquartier.com/cqpm-loi` direkt:
1. IONOS → **Hosting → SFTP & SSH** → Zugangsdaten anzeigen (Server, Benutzer, Passwort).
2. Mit einem SFTP-Programm (z. B. FileZilla oder Cyberduck) verbinden.
3. Im Hauptordner der Website (dort, wo bei WordPress `wp-config.php` liegt) einen Ordner **`cqpm-loi`** anlegen.
4. Den Inhalt von `loi-seite/` hineinkopieren: `index.html` (oder `cinematic.html`, umbenannt in `index.html`) und den Ordner `assets/`.
   Nicht nötig: `*.md`, `*.py`, `*.gs`.
5. Aufrufen: `https://cashflowquartier.com/cqpm-loi/`

## B) IONOS Website-Baukasten („MyWebsite“)
Dort kann man keine eigenen Ordner hochladen. Dann:
1. Die Seite auf einem kostenlosen Webspace hosten (z. B. Cloudflare Pages oder Netlify; Claude bereitet das vor).
2. Bei IONOS unter **Domains → cashflowquartier.com → DNS** eine Subdomain **`cqpm-loi`** als CNAME auf die Hosting-Adresse anlegen.
3. Aufrufen: `https://cqpm-loi.cashflowquartier.com`
Optional verlinkt die Hauptseite per Weiterleitung von `/cqpm-loi` dorthin (im Baukasten unter Einstellungen → Weiterleitungen, falls verfügbar).

## Video mit einem Klick
Liegt das Video als eigene Datei auf demselben Webspace, startet es mit einem Klick sofort und ohne Google.
1. Video verkleinern (720p, ca. 50–80 MB statt 232 MB):
   `ffmpeg -i CQPM_Video.mp4 -vf scale=-2:720 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 96k -movflags +faststart assets/cqpm-video.mp4`
2. Datei nach `cqpm-loi/assets/` hochladen.
3. In `index.html` beim Player `data-mp4="assets/cqpm-video.mp4"` eintragen.
Alternative: Video bei Vimeo hochladen und die Vimeo-ID bei `data-vimeo="…"` eintragen.
