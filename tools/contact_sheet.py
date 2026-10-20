"""Kontaktabzug (Übersichtsbild) aller Fotos eines Ordners, um Bilder auszuwählen.

  python tools/contact_sheet.py <bildordner> <ausgabe.jpg>

Unter jedem Bild stehen die ersten 6 Zeichen des Dateinamens (= Drive-ID).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def main(argv=None):
    args = argv or sys.argv[1:]
    if len(args) != 2:
        print(__doc__)
        return 2
    fs = sorted(p for p in Path(args[0]).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not fs:
        print("keine Bilder gefunden")
        return 1
    w, h, spalten = 240, 320, min(len(fs), 6)
    zeilen = (len(fs) + spalten - 1) // spalten
    sheet = Image.new("RGB", (w * spalten, (h + 14) * zeilen), "white")
    for i, f in enumerate(fs):
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im.thumbnail((w - 4, h - 4))
        x, y = (i % spalten) * w, (i // spalten) * (h + 14)
        sheet.paste(im, (x + 2, y + 2))
        ImageDraw.Draw(sheet).text((x + 4, y + h), f.stem[:6], fill="red")
    sheet.save(args[1], quality=60)
    print(args[1], [f.stem[:6] for f in fs])
    return 0


if __name__ == "__main__":
    sys.exit(main())
