"""Gespeicherte Drive-Downloads (tool-results/*.txt mit JSON {content, id, title}) in echte Dateien umwandeln.

`mcp__Google_Drive__download_file_content` legt große Antworten als JSON-Datei unter tool-results/ ab.
Dieses Skript sucht dort die Datei zu einer Drive-ID und schreibt den dekodierten Inhalt in ein Zielverzeichnis.

  python tools/drive_decode.py <zielordner> <drive-id> [<drive-id> ...]
  python tools/drive_decode.py <zielordner> --all        # alle noch nicht dekodierten Downloads
"""
from __future__ import annotations

import base64
import glob
import json
import os
import re
import sys
from pathlib import Path

TOOL_RESULTS = os.environ.get(
    "CLAUDE_TOOL_RESULTS",
    max(glob.glob("/root/.claude/projects/*/*/tool-results"), key=os.path.getmtime, default=""),
)


def _downloads():
    for f in glob.glob(os.path.join(TOOL_RESULTS, "mcp-Google_Drive-download_file_content-*.txt")):
        try:
            d = json.loads(Path(f).read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(d, dict) and d.get("content") and d.get("id"):
            yield d


def _endung(d):
    titel = d.get("title") or ""
    ext = Path(titel).suffix
    if not ext:
        ext = {"image/jpeg": ".jpg", "image/png": ".png", "application/pdf": ".pdf",
               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx"}.get(d.get("mimeType"), "")
    return ext.lower()


def main(argv=None):
    args = argv or sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        return 2
    ziel = Path(args[0])
    ziel.mkdir(parents=True, exist_ok=True)
    gesucht = None if args[1] == "--all" else set(args[1:])
    gefunden = set()
    for d in _downloads():
        if gesucht is not None and d["id"] not in gesucht:
            continue
        out = ziel / f"{d['id']}{_endung(d)}"
        out.write_bytes(base64.b64decode(d["content"]))
        gefunden.add(d["id"])
        titel = re.sub(r"\s+", " ", d.get("title", ""))
        print(f"{out}  ({titel})")
    if gesucht:
        for fehlend in sorted(gesucht - gefunden):
            print(f"FEHLT: {fehlend} (erst mit download_file_content laden)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
