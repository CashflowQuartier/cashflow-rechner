"""HTML-Teaser rendern und per Headless-Chromium als PDF drucken."""
from __future__ import annotations

import base64
import mimetypes
import re
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageOps

from . import finance

TEMPLATES = Path(__file__).parent / "templates"
ASSETS = Path(__file__).parent / "assets"
FONT_WEIGHTS = (400, 500, 600, 700, 800)
CHROMIUM_CANDIDATES = [
    os.environ.get("CHROMIUM_PATH", ""),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
    shutil.which("google-chrome") or "",
]
RENO_BILDER_SCHWELLE = 5000  # ab dieser Reno-Rückstellung SE werden Visualisierungen gezeigt


def eur(v, nachkomma=0):
    if v is None:
        return "–"
    s = f"{v:,.{nachkomma}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def num(v, nachkomma=2):
    if v is None:
        return "–"
    return f"{v:,.{nachkomma}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v, nachkomma=1):
    return "–" if v is None else num(v * 100, nachkomma) + " %"


def signed_eur(v, nachkomma=0):
    return ("+ " if v > 0.005 else "− " if v < -0.005 else "") + eur(abs(v), nachkomma)


def image_data_uri(path: str | Path, max_px: int = 1600, quality: int = 82) -> str:
    """Bild verkleinern, EXIF-Rotation anwenden und als data-URI einbetten."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im.thumbnail((max_px, max_px))
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    im.save(tmp.name, "JPEG", quality=quality, optimize=True)
    data = base64.b64encode(Path(tmp.name).read_bytes()).decode()
    os.unlink(tmp.name)
    return f"data:image/jpeg;base64,{data}"


def logo_data_uri(path: str | Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def font_face_css() -> str:
    """Onest (Hausschrift der Website) als eingebettete @font-face-Regeln."""
    rules = []
    for w in FONT_WEIGHTS:
        f = ASSETS / "fonts" / f"onest-latin-{w}-normal.woff2"
        if f.exists():
            data = base64.b64encode(f.read_bytes()).decode()
            rules.append(f"@font-face{{font-family:'Onest';font-weight:{w};font-style:normal;"
                         f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "\n".join(rules)


def subvention_chart_svg(stufen, soll_qm, ist_qm, width=640, height=180) -> str:
    """Treppendiagramm: gesetzliche Miete (€/m²) je Stufe vs. SOLL-Miete, Differenz = Subvention."""
    if not stufen:
        return ""
    total = stufen[-1].bis_monat
    ml, mr, mt, mb = 44, 12, 14, 34
    w, h = width - ml - mr, height - mt - mb
    ymax = soll_qm * 1.12
    x = lambda m: ml + m / total * w
    y = lambda v: mt + h - v / ymax * h
    parts = [f'<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="Mietsubvention bis zur SOLL-Miete">']
    for t in range(0, int(ymax) + 1, 2):
        parts.append(f'<line x1="{ml}" x2="{width-mr}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="grid"/>')
        parts.append(f'<text x="{ml-6}" y="{y(t)+3:.1f}" class="ax" text-anchor="end">{t}</text>')
    for s in stufen:
        x0, x1 = x(s.von_monat), x(s.bis_monat)
        parts.append(f'<rect x="{x0+1:.1f}" y="{y(s.miete_qm):.1f}" width="{x1-x0-2:.1f}" height="{y(0)-y(s.miete_qm):.1f}" class="bar-ist"/>')
        parts.append(f'<rect x="{x0+1:.1f}" y="{y(soll_qm):.1f}" width="{x1-x0-2:.1f}" height="{y(s.miete_qm)-y(soll_qm):.1f}" class="bar-sub"/>')
        parts.append(f'<text x="{(x0+x1)/2:.1f}" y="{y(s.miete_qm)-4:.1f}" class="lbl-sub" text-anchor="middle">{num(s.miete_qm)}</text>')
        parts.append(f'<text x="{(x0+x1)/2:.1f}" y="{height-mb+14}" class="ax" text-anchor="middle">Monat {s.von_monat+1}–{s.bis_monat}</text>')
    parts.append(f'<line x1="{ml}" x2="{width-mr}" y1="{y(soll_qm):.1f}" y2="{y(soll_qm):.1f}" class="soll"/>')
    parts.append(f'<text x="{width-mr}" y="{y(soll_qm)-5:.1f}" class="lbl-soll" text-anchor="end">SOLL-Miete {num(soll_qm)} €/m²</text>')
    parts.append(f'<text x="{ml-34}" y="{mt-2}" class="ax">€/m²</text>')
    parts.append("</svg>")
    return "".join(parts)


LAGE_ABK = [(r"\bre\.?$", "rechts"), (r"\bli\.?$", "links"), (r"\bre\.", "rechts"), (r"\bli\.", "links")]


def wohnungstitel(adresse: str, stadt: str) -> dict:
    """'Freiligrathstr. 8 EG re.' -> Straße 'Freiligrathstraße 8', Wohnung 'EG rechts', Stadt."""
    m = re.match(r"^(.*?\d+\s?[a-zA-Z]?)\s+(.*)$", adresse.strip())
    strasse, lage = (m.group(1), m.group(2)) if m else (adresse, "")
    strasse = re.sub(r"str\.(?=\s|$)", "straße", strasse)
    for pat, rep in LAGE_ABK:
        lage = re.sub(pat, rep, lage)
    lage = lage.strip()
    return {"strasse": strasse, "wohnung": f"Wohnung {lage}" if lage else "Wohnung", "stadt": stadt,
            "voll": " · ".join(x for x in (strasse, f"Wohnung {lage}" if lage else "", stadt) if x)}


def team_bilder(team: list[dict]) -> list[dict]:
    out = []
    for t in team or []:
        t = dict(t)
        bild = t.get("bild")
        pfad = (ASSETS / "team" / bild) if bild and not Path(bild).is_absolute() else (Path(bild) if bild else None)
        t["foto"] = image_data_uri(pfad, 500, 80) if pfad and pfad.exists() else None
        t["initialen"] = "".join(w[0] for w in t["name"].split()[:2]).upper()
        out.append(t)
    return out


def marktvergleich(preise: dict, unser_kauf_qm: float, soll_qm: float) -> dict:
    """Ø je Quelle; Box nur zeigen, wenn der Markt über unserem Preis bzw. auf/über der SOLL-Miete liegt."""
    out = {}
    for key, unser, besser in (("kauf", unser_kauf_qm, lambda m, x: m > x), ("miete", soll_qm, lambda m, x: m >= x)):
        cfg = (preise or {}).get(key) or {}
        werte = [q["wert"] for q in cfg.get("quellen", []) if q.get("wert")]
        if not werte:
            continue
        mittel = sum(werte) / len(werte)
        out[key] = {"label": cfg.get("label", ""), "mittel": mittel, "quellen": cfg.get("quellen", []),
                    "zeigen": besser(mittel, unser)}
    return out


def build_context(project, unit, facts: dict, photos: list[str], renders: list[str], cover: str | None,
                  logo: str | None = None) -> dict:
    p = project.params
    u = dict(unit)
    stufen = finance.subvention_staffel(u)
    monat = finance.monat_jahr1(u, p)
    proj = finance.projektion(u, p, jahre=10)
    fl = u["flaeche"]
    ist_qm = u["ist_miete"] / fl
    soll_qm = u.get("soll_qm") or u["soll_qm_vorgabe"]
    vermietet = str(u.get("status", "")).lower().startswith("vermietet")
    house_key = next((k for k in facts.get("haeuser", {}) if k.lower() in u["adresse"].lower()), None)
    haus = facts.get("haeuser", {}).get(house_key, {}) if house_key else {}
    reno_se = u.get("reno_se") or 0
    return dict(
        f=facts,
        haus=haus,
        u=u,
        p=p,
        project=project,
        vermietet=vermietet,
        flaeche=fl,
        ist_qm=ist_qm,
        soll_qm=soll_qm,
        stufen=stufen,
        subvention=sum(s.zuschuss_gesamt for s in stufen) + (u.get("subvention_zusatz") or 0),
        subvention_monate=stufen[-1].bis_monat if stufen else 0,
        subvention_start=stufen[0].zuschuss_monat if stufen else 0,
        chart=subvention_chart_svg(stufen, soll_qm, ist_qm),
        monat=monat,
        proj=proj,
        tilgung_10j=sum(r.tilgung for r in proj),
        steuer_10j=sum(r.steuer for r in proj),
        cf_10j=sum(r.cf_nach_steuer for r in proj),
        rendite_gesamt=u["miete_soll"] * 12 / u["kaufpreis"],
        rendite_netto=u["miete_soll"] * 12 / u["kaufpreis_netto"] if u.get("kaufpreis_netto") else None,
        bodenanteil=finance.bodenanteil(u, p),
        afa_jahr=finance.afa_jahr(u, p),
        afa_satz=1 / p.rnd_jahre,
        werbungskosten=finance.WERBUNGSKOSTEN_PAUSCHAL,
        reno_se=reno_se,
        zeige_reno_bilder=reno_se > RENO_BILDER_SCHWELLE and bool(renders),
        weg_anteil=u.get("sanierung_weg") or 0,
        weg=project.weg_massnahmen,
        weg_summe=project.weg_summe,
        se=project.se_massnahmen,
        photos=[image_data_uri(x) for x in photos],
        renders=[image_data_uri(x) for x in renders],
        cover=image_data_uri(cover, 2000) if cover else None,
        logo=logo_data_uri(logo or ASSETS / "logo_navy.png"),
        logo_white=logo_data_uri(ASSETS / "logo_white.png"),
        font_css=font_face_css(),
        titel=wohnungstitel(u["adresse"], facts.get("objekt", {}).get("stadt", "")),
        steuer=finance.steuerrechnung(u, p),
        bilanz=finance.vermoegensbilanz(u, p),
        team=team_bilder(facts.get("team")),
        markt=marktvergleich(facts.get("lage", {}).get("preise"), u["kaufpreis_netto"] / fl, soll_qm),
        mietrecht=facts.get("mietrecht", {"kappungsgrenze": 0.20}),
    )


def render_html(ctx: dict) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]))
    env.filters.update(eur=eur, num=num, pct=pct, signed_eur=signed_eur)
    return env.get_template("teaser.html").render(**ctx)


def html_to_pdf(html: str, out_pdf: str | Path) -> Path:
    chrome = next((c for c in CHROMIUM_CANDIDATES if c and Path(c).exists()), None)
    if not chrome:
        raise RuntimeError("Kein Chromium gefunden (CHROMIUM_PATH setzen)")
    out_pdf = Path(out_pdf).resolve()
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "teaser.html"
        src.write_text(html, encoding="utf-8")
        subprocess.run(
            [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={out_pdf}", src.as_uri()],
            check=True, capture_output=True, timeout=120,
        )
    return out_pdf
