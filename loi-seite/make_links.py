"""Erzeugt personalisierte LOI-Links aus einer CSV-Empfängerliste.

CSV-Spalten (Kopfzeile): id, firma, anrede, name, position, email, typ
  id     – eindeutiges Kürzel, z. B. fo-mustermann (landet im LOI als ref_id)
  anrede – Herr / Frau / leer

Aufruf:
  python loi-seite/make_links.py empfaenger.csv --base https://cashflowquartier.com/verwaltung/ > links.csv
"""
import argparse, base64, csv, json, sys

KEYS = {"id": "id", "firma": "f", "anrede": "a", "name": "n", "position": "p", "email": "e", "typ": "t"}


def token(row):
    data = {short: row[col].strip() for col, short in KEYS.items() if row.get(col, "").strip()}
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--base", default="https://cashflowquartier.com/verwaltung/")
    a = ap.parse_args()
    out = csv.writer(sys.stdout)
    out.writerow(["id", "firma", "name", "email", "link"])
    with open(a.csv, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            t = token(row)
            out.writerow([row.get("id", ""), row.get("firma", ""), row.get("name", ""), row.get("email", ""), f"{a.base}?r={t}"])


if __name__ == "__main__":
    main()
