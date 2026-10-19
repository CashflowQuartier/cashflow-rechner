"""Teaser-PDF für eine Einheit erzeugen.

Beispiel:
  python -m teaser_generator.cli \\
      --pe "PE - Freiligrathstr.xlsx" --facts projects/freiligrathstr-oberhausen/facts.yaml \\
      --unit 33 --cover assets/aussen.jpg --photos assets/we33/*.jpg --renders assets/we33/reno/*.jpg \\
      --out out/Teaser_WE33.pdf

  python -m teaser_generator.cli --pe ... --list      # alle Einheiten der PE-Excel anzeigen
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from . import pe_excel, render


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pe", required=True, help="Pfad zur PE-Excel")
    ap.add_argument("--facts", help="facts.yaml des Projekts")
    ap.add_argument("--unit", help="WE-Nr., Einheit-Nr. oder Adresse (z. B. 'Freiligrathstr. 8 EG re.')")
    ap.add_argument("--cover", help="Titelbild (Außenansicht)")
    ap.add_argument("--photos", nargs="*", default=[], help="Ist-Fotos der Wohnung")
    ap.add_argument("--renders", nargs="*", default=[], help="Visualisierungen renoviert")
    ap.add_argument("--logo", help="Logo (PNG/SVG)")
    ap.add_argument("--out", help="Ziel-PDF")
    ap.add_argument("--html", help="zusätzlich HTML speichern")
    ap.add_argument("--list", action="store_true", help="Einheiten auflisten")
    a = ap.parse_args(argv)

    project = pe_excel.load(a.pe)
    if a.list:
        for u in project.units:
            print(f"WE {int(u['we_nr']):>3}  {u['adresse']:<32} {u['flaeche']:>6.2f} m²  KP {u['kaufpreis']:>9,.0f} €  "
                  f"Subv. {u['subvention']:>8,.0f} €  Reno SE {u['reno_se'] or 0:>8,.0f} €  {u['status']}")
        return 0
    if not (a.unit and a.facts and a.out):
        ap.error("--unit, --facts und --out sind erforderlich")

    facts = yaml.safe_load(Path(a.facts).read_text(encoding="utf-8"))
    unit = project.unit(a.unit)
    kappung = (facts.get("mietrecht") or {}).get("kappungsgrenze")
    if kappung and unit.get("erh1_qm") and unit.get("ist_miete"):
        faktor = unit["erh1_qm"] / (unit["ist_miete"] / unit["flaeche"])
        if abs(faktor - (1 + kappung)) > 0.005:
            print(f"WARNUNG: PE-Excel rechnet mit {faktor - 1:.0%} je Erhöhungsschritt, vor Ort gilt eine Kappungsgrenze "
                  f"von {kappung:.0%} – Subvention in der Excel prüfen!", file=sys.stderr)
    ctx = render.build_context(project, unit, facts, a.photos, a.renders, a.cover, a.logo)
    html = render.render_html(ctx)
    if a.html:
        Path(a.html).write_text(html, encoding="utf-8")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pdf = render.html_to_pdf(html, a.out)
    print(f"Teaser erstellt: {pdf}")
    if unit.get("reno_se", 0) > render.RENO_BILDER_SCHWELLE and not a.renders:
        print(f"Hinweis: Reno-Rückstellung > {render.RENO_BILDER_SCHWELLE} € – Visualisierungen fehlen (--renders).",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
