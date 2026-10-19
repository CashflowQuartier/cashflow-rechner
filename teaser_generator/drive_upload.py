"""Dateien über den Upload-Briefkasten (Google Apps Script, siehe tools/drive_upload.gs) in einen Drive-Ordner legen.

Erwartet die Umgebungsvariablen CFQ_DRIVE_UPLOAD_URL (Web-App-URL) und CFQ_DRIVE_UPLOAD_TOKEN.

  python -m teaser_generator.drive_upload <ordner-id> <datei> [<datei> ...]
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import urllib.request
from pathlib import Path


def upload(ordner_id: str, pfad: str | Path, name: str | None = None) -> dict:
    url = os.environ.get("CFQ_DRIVE_UPLOAD_URL")
    token = os.environ.get("CFQ_DRIVE_UPLOAD_TOKEN")
    if not url or not token:
        raise RuntimeError("CFQ_DRIVE_UPLOAD_URL / CFQ_DRIVE_UPLOAD_TOKEN fehlen in der Umgebung")
    pfad = Path(pfad)
    body = json.dumps({
        "token": token,
        "folderId": ordner_id,
        "name": name or pfad.name,
        "mimeType": mimetypes.guess_type(pfad.name)[0] or "application/octet-stream",
        "data": base64.b64encode(pfad.read_bytes()).decode(),
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:  # Apps Script antwortet nach Redirect mit JSON
        antwort = json.loads(r.read().decode())
    if not antwort.get("ok"):
        raise RuntimeError(f"Upload fehlgeschlagen: {antwort}")
    return antwort


def main(argv=None):
    args = (argv or sys.argv[1:])
    if len(args) < 2:
        print(__doc__)
        return 2
    ordner, dateien = args[0], args[1:]
    for d in dateien:
        a = upload(ordner, d)
        print(f"{Path(d).name} -> {a['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
