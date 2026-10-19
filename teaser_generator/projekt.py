"""Projekt-Teaser: ein PDF für alle Einheiten eines Projekts.

Allgemeine Infos (Objekt, Sanierung, Lage, Konzept, Team), eine Beispielrechnung für eine
Wohnung und eine Preisliste über alle Einheiten der PE-Excel. Die Seiten Cashflow, Lage,
Konzept, Zusammenfassung und Team sind dieselben wie im Wohnungs-Teaser (templates/_seite_*.html).
"""
from __future__ import annotations

import re

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import finance, render

# Zeilen je Preislisten-Seite (Hauszeilen zählen mit); die erste Seite hat Überschrift und Erläuterung
PREISLISTE_ZEILEN_ERSTE = 34
PREISLISTE_ZEILEN = 39
GALERIE_RATIO = 58.3 / 44


def haus_und_lage(adresse: str) -> tuple[str, str]:
    """'Tannenbergstr. 6 1. OG Links' -> ('Tannenbergstr. 6', '1. OG links')."""
    m = re.match(r"^(.*?\d+\s?[a-zA-Z]?)\s+(.*)$", adresse.strip())
    haus, lage = (m.group(1), m.group(2)) if m else (adresse, "")
    lage = re.sub(r"\b(Links|Rechts|Mitte)\b", lambda x: x.group(1).lower(), lage)
    return haus, lage


def art(u: dict) -> str:
    status = str(u.get("status") or "").lower()
    if "gewerbe" in status:
        return "Gewerbe"
    return "Haus" if "alleinstehend" in str(u["adresse"]).lower() else "Wohnung"


def einheiten(project) -> list[dict]:
    p = project.params
    rows = []
    for u in project.units:
        haus, lage = haus_und_lage(u["adresse"])
        m = finance.monat_jahr1(u, p)
        rows.append(dict(
            u=u, haus=haus, lage=lage.replace("Alleinstehend", "freistehend"), art=art(u),
            vermietet="vermietet" in str(u.get("status") or "").lower(),
            leer="leer" in str(u.get("status") or "").lower(),
            qm_preis=u["kaufpreis"] / u["flaeche"],
            cf=m.cf_nach_steuer,
        ))
    return rows


def haeuser(rows: list[dict]) -> list[dict]:
    out = {}
    for r in rows:
        h = out.setdefault(r["haus"], {"haus": r["haus"], "rows": []})
        h["rows"].append(r)
    for h in out.values():
        rs = h["rows"]
        h.update(
            anzahl=len(rs),
            wohnungen=sum(1 for r in rs if r["art"] != "Gewerbe"),
            gewerbe=sum(1 for r in rs if r["art"] == "Gewerbe"),
            flaeche=sum(r["u"]["flaeche"] for r in rs),
            qm_min=min(r["u"]["flaeche"] for r in rs), qm_max=max(r["u"]["flaeche"] for r in rs),
            kp_min=min(r["u"]["kaufpreis"] for r in rs), kp_max=max(r["u"]["kaufpreis"] for r in rs),
            vermietet=sum(1 for r in rs if r["vermietet"]),
        )
    return list(out.values())


def preisliste_seiten(hs: list[dict]) -> list[list[dict]]:
    """Hausweise auf Seiten verteilen; ein Haus wird nicht auf zwei Seiten zerrissen."""
    seiten, akt, n = [], [], 0
    for h in hs:
        bedarf = len(h["rows"]) + 1
        zeilen = PREISLISTE_ZEILEN if seiten else PREISLISTE_ZEILEN_ERSTE
        if akt and n + bedarf > zeilen:
            seiten.append(akt)
            akt, n = [], 0
        akt.append(h)
        n += bedarf
    if akt:
        seiten.append(akt)
    return seiten


def build_context(project, beispiel_unit, facts: dict, cover: str | None, galerie: list[str],
                  photos: list[str] | None = None) -> dict:
    ctx = render.build_context(project, beispiel_unit, facts, photos or [], [], cover)
    rows = einheiten(project)
    hs = haeuser(rows)
    seiten = preisliste_seiten(hs)
    wohnen = [r for r in rows if r["art"] != "Gewerbe"]
    pt = facts.get("projekt", {})
    stadt = facts.get("objekt", {}).get("stadt", "")
    titel = pt.get("titel") or project.titel
    n_vor = 3  # Cover, Objekt, Sanierung
    seite_nr = {"cashflow": n_vor + 1, "konzept": n_vor + 2}
    seite_nr["preisliste"] = n_vor + 3
    n = seite_nr["preisliste"] + len(seiten)
    seite_nr.update(lage=n, zusammenfassung=n + 1, team=n + 2)
    ctx.update(
        projekt=pt,
        beispiel=True,
        beispiel_lage=" · ".join(haus_und_lage(beispiel_unit["adresse"])),
        titel={"strasse": titel, "wohnung": "", "stadt": stadt, "voll": f"{titel} · {stadt}" if stadt else titel},
        rows=rows,
        haeuser=hs,
        preisliste=seiten,
        seite_nr=seite_nr,
        anzahl=len(rows),
        anzahl_wohnen=len(wohnen),
        anzahl_gewerbe=len(rows) - len(wohnen),
        anzahl_vermietet=sum(1 for r in rows if r["vermietet"]),
        flaeche_gesamt=sum(r["u"]["flaeche"] for r in rows),
        qm_min=min(r["u"]["flaeche"] for r in wohnen), qm_max=max(r["u"]["flaeche"] for r in wohnen),
        kp_min=min(r["u"]["kaufpreis"] for r in wohnen), kp_max=max(r["u"]["kaufpreis"] for r in wohnen),
        cf_min=min(r["cf"] for r in rows), cf_max=max(r["cf"] for r in rows),
        volumen=sum(r["u"]["kaufpreis"] for r in rows),
        subvention_gesamt=sum(r["u"].get("subvention") or 0 for r in rows),
        reno_gesamt=sum(r["u"].get("reno_se") or 0 for r in rows),
        knk_gesamt=sum(r["u"].get("knk") or 0 for r in rows),
        galerie=[render.image_data_uri(x, 1200, ratio=GALERIE_RATIO) for x in galerie],
    )
    if not ctx["se"] and pt.get("reno_standard"):
        ctx["se"] = [{"name": x} for x in pt["reno_standard"]]
    return ctx


def render_html(ctx: dict) -> str:
    env = Environment(loader=FileSystemLoader(render.TEMPLATES), autoescape=select_autoescape(["html"]))
    env.filters.update(eur=render.eur, num=render.num, pct=render.pct, signed_eur=render.signed_eur)
    return env.get_template("projekt.html").render(**ctx)
