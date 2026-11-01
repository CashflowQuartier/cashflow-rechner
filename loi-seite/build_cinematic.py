"""Erzeugt cinematic.html aus index.html (gleicher Inhalt, gleiches Formular, anderer Look).

Nach jeder Textänderung in index.html einmal ausführen:
  python loi-seite/build_cinematic.py
Der Look steckt in assets/cinematic.css und assets/cinematic.js.
"""
from pathlib import Path

here = Path(__file__).parent
s = (here / "index.html").read_text(encoding="utf-8")
s = s.replace("</style>", "</style>\n<link rel=\"stylesheet\" href=\"assets/cinematic.css\">", 1)
s = s.replace("</title>", " (Cinematic)</title>", 1)
s = s.replace("</body>", "<script src=\"assets/cinematic.js\"></script>\n</body>", 1)
(here / "cinematic.html").write_text(s, encoding="utf-8")
print("cinematic.html aktualisiert")
