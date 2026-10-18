"""Rechenlogik: Mietsubvention (Staffel bis zur SOLL-Miete) und Käufer-Cashflow.

Die Formeln bilden die PE-Excel nach (Spalten O, AQ–AY), damit Teaser und
Kalkulation dieselben Zahlen zeigen. Die 10-Jahres-Vorschau ist eine
Erweiterung (Annuitätendarlehen, Miete konstant auf SOLL-Niveau).
"""
from __future__ import annotations

from dataclasses import dataclass

from .pe_excel import Params

# Pauschale sonstige Werbungskosten p.m. in der Steuerformel der PE-Excel (Spalte AX: "-20")
WERBUNGSKOSTEN_PAUSCHAL = 20.0
# Mieterhöhungsrhythmus aus der PE-Excel: 6 Monate bis zur 1. Erhöhung, danach alle 36 Monate +20 %
ERSTE_ERHOEHUNG_MONATE = 6
ERHOEHUNG_INTERVALL_MONATE = 36


@dataclass
class SubventionsStufe:
    von_monat: int
    bis_monat: int
    miete_qm: float
    soll_qm: float
    flaeche: float

    @property
    def monate(self):
        return self.bis_monat - self.von_monat

    @property
    def zuschuss_monat(self):
        return max(self.soll_qm - self.miete_qm, 0) * self.flaeche

    @property
    def zuschuss_gesamt(self):
        return self.zuschuss_monat * self.monate


def subvention_staffel(u: dict) -> list[SubventionsStufe]:
    """Rekonstruiert die Mieterhöhungsstaffel der PE-Excel (Spalten J–O)."""
    fl = u["flaeche"]
    soll = u.get("soll_qm") or u["soll_qm_vorgabe"]
    ist_qm = u["ist_miete"] / fl
    stufen_qm = [ist_qm, u["erh1_qm"], u["erh2_qm"], u["erh3_qm"]]
    dauer = [ERSTE_ERHOEHUNG_MONATE] + [ERHOEHUNG_INTERVALL_MONATE] * 3
    out, m = [], 0
    for qm, d in zip(stufen_qm, dauer):
        if qm >= soll:
            break
        out.append(SubventionsStufe(m, m + d, qm, soll, fl))
        m += d
    return out


@dataclass
class Monatsrechnung:
    miete: float
    zins: float
    tilgung: float
    hv: float
    mv: float
    sonstige: float
    ruecklage: float
    afa: float
    steuer: float

    @property
    def bankrate(self):
        return self.zins + self.tilgung

    @property
    def bewirtschaftung(self):
        return self.hv + self.mv + self.sonstige + self.ruecklage

    @property
    def cf_vor_steuer(self):
        return self.miete - self.bankrate - self.bewirtschaftung

    @property
    def cf_nach_steuer(self):
        return self.cf_vor_steuer + self.steuer


def bodenanteil(u: dict, p: Params) -> float:
    return p.grundstueck_qm * p.bodenrichtwert / p.gesamtflaeche * u["flaeche"]


def afa_jahr(u: dict, p: Params) -> float:
    return (u["kaufpreis"] - bodenanteil(u, p)) / p.rnd_jahre


def steuereffekt(miete, zins, hv, mv, sonstige, afa, p: Params, werbungskosten=WERBUNGSKOSTEN_PAUSCHAL):
    """Positiv = Steuererstattung (Formel Spalte AX der PE-Excel)."""
    return -(miete - zins - hv - mv - afa - sonstige - werbungskosten) * p.grenzsteuer


def monat_jahr1(u: dict, p: Params) -> Monatsrechnung:
    kp = u["kaufpreis"]
    miete = u["miete_soll"]
    zins = kp * p.zins / 12
    tilg = kp * p.tilgung / 12
    afa = afa_jahr(u, p) / 12
    st = steuereffekt(miete, zins, u["hv"], u["mv"], u["sonstige"], afa, p)
    return Monatsrechnung(miete, zins, tilg, u["hv"], u["mv"], u["sonstige"], u["ruecklage"], afa, st)


@dataclass
class Jahreszeile:
    jahr: int
    miete: float
    zins: float
    tilgung: float
    bewirtschaftung: float
    afa: float
    steuer: float
    restschuld: float

    @property
    def cf_vor_steuer(self):
        return self.miete - self.zins - self.tilgung - self.bewirtschaftung

    @property
    def cf_nach_steuer(self):
        return self.cf_vor_steuer + self.steuer


def projektion(u: dict, p: Params, jahre: int = 10) -> list[Jahreszeile]:
    """Annuitätendarlehen über den beurkundeten Kaufpreis (100 %), Miete konstant auf SOLL."""
    schuld = u["kaufpreis"]
    rate = schuld * (p.zins + p.tilgung) / 12
    afa_m = afa_jahr(u, p) / 12
    miete = u["miete_soll"]
    rows = []
    for j in range(1, jahre + 1):
        zins_j = tilg_j = steuer_j = 0.0
        for _ in range(12):
            z = schuld * p.zins / 12
            t = rate - z
            schuld -= t
            zins_j += z
            tilg_j += t
            steuer_j += steuereffekt(miete, z, u["hv"], u["mv"], u["sonstige"], afa_m, p)
        bew = (u["hv"] + u["mv"] + u["sonstige"] + u["ruecklage"]) * 12
        rows.append(Jahreszeile(j, miete * 12, zins_j, tilg_j, bew, afa_m * 12, steuer_j, schuld))
    return rows
