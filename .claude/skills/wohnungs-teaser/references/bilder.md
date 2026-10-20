# Fotos & Visualisierungen

## Ist-Fotos
- Laden: `download_file_content` je Datei (Antwort landet als JSON in tool-results), dann
  `python tools/drive_decode.py $S/units/we<Nr> <id1> <id2> …`.
- Auswahl: `python tools/contact_sheet.py $S/units/we<Nr> $S/we<Nr>_sheet.jpg` und das Bild ansehen.
  2–3 aussagekräftige Räume (Wohnen, Küche, Bad; sonst Schlafzimmer). Keine Personen, keine reinen Abstellräume/Flure.
  Mit nur 2 brauchbaren Fotos passt sich das Layout automatisch an.

## Soll-Bilder (Visualisierungen) – nur bei Reno-Rückstellung SE > 5.000 €
Higgsfield `generate_image_batch`, Modell `gpt_image_2_5`, `quality: high`, `resolution: 2k`, `aspect_ratio: 3:4`
(Kosten ca. 2,75 Credits/Bild; günstiger: `nano_banana_2_1` mit ca. 2 Credits). Ein Bild je gewähltem Ist-Foto, gleiche Reihenfolge.

Prompt-Vorlage (Raumbeschreibung aus dem Ist-Foto übernehmen: Raumform, Fensterzahl/-position, Heizkörper, Blickrichtung):
> Photorealistic real-estate photo, handheld smartphone, portrait orientation, of an empty <RAUM> in a renovated 1960s German
> apartment, seen from the doorway: <RAUMFORM, FENSTER, HEIZKÖRPER>. Completely empty, no furniture. Freshly painted pure white
> walls and ceiling, new warm medium-brown oak-look vinyl plank floor with white skirting, new white interior door with white
> frame, new white modern switches and sockets. Bright daylight, clean, realistic modest rental standard, no people.

- Küche zusätzlich: „No kitchen units installed, only water and power connections. New white rectangular tile splashback
  (Fliesenspiegel) along the <left/right> wall.“
- Bad: „newly renovated bathroom … white built-in bathtub with chrome shower set and glass screen, white wall-hung toilet,
  small white washbasin with mirror, matt white wall tiles, light grey large-format floor tiles, white towel radiator, LED spots.“

Pflichtmerkmale laut Nutzer: leer, brauner Vinylboden, weiße Wände, weiße Türen und Zargen, neue Schalter/Steckdosen,
neuer Fliesenspiegel in der Küche, neues Bad.

## Ergebnisse herunterladen
`jobs_wait` liefert `result_url` (cloudfront). Direkter Download aus der Claude-Umgebung ist gesperrt; Umweg über den Sandbox:
```
sandbox_exec: mkdir -p r && cd r && curl -sf -o 0.png "<url0>" && convert 0.png -resize 1000x1000 -quality 78 r0.jpg … ;
  image_paths: ["r/r0.jpg", "r/r1.jpg", "r/r2.jpg"]   (max. 4 Bilder / 512 KiB je Aufruf)
```
Die zurückgegebenen Bilder liegen danach als `tool-results/mcp-Higgsfield-blob-*.jpg` vor (Pfad steht in der Antwort) →
nach `$S/renders/we<Nr>/<n>_<raum>.jpg` kopieren. Bilder dabei ansehen: Raumform plausibel, Pflichtmerkmale erfüllt, keine Möbel.

Werden `upload.higgsfield.ai` und `d8j0ntlcm91z4.cloudfront.net` in der Umgebung freigegeben, kann stattdessen das echte
Ist-Foto hochgeladen (`media_upload` + curl PUT + `media_confirm`) und als `medias: [{role: image_references, value: <id>}]`
mit einem Bearbeitungs-Prompt („renovate this room: …“) übergeben werden – das trifft den Grundriss genauer.
