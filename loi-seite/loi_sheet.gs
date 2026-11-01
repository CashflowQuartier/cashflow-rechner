/**
 * LOI-Eingang für die Seite cashflowquartier.com/verwaltung
 *
 * Nimmt jedes abgeschickte LOI als JSON an und
 *   1. schreibt es als Zeile in das Blatt „LOIs“ (eine Zeile je Absichtserklärung),
 *   2. schreibt jeden Standort als Zeile in das Blatt „Standorte“ (für die Auswertung nach Region),
 *   3. schickt dem Absender eine Bestätigung mit PDF, unterschrieben von Jan-Moritz Becker,
 *   4. schickt eine Kopie an BENACHRICHTIGUNG.
 *
 * Einrichtung: siehe loi-seite/LOI_SHEET.md
 */

const BENACHRICHTIGUNG = 'kontakt@cashflowquartier.com';
const ABSENDER_NAME = 'Jan-Moritz Becker · Cashflow Quartier';
const BESTAETIGUNG_SENDEN = true;

const KOPF_LOIS = [
  'Eingegangen', 'Ref-ID', 'Unternehmen', 'Art', 'Name', 'Position', 'Entscheider', 'E-Mail', 'Telefon',
  'HV Einheiten', 'HV Objekte', 'HV Preis-Feedback (29 €)',
  'SEV Einheiten', 'SEV WEGs', 'SEV Preis-Feedback (35–55 €)',
  'Einheiten gesamt', 'Standorte', 'Frühester Start', 'Verwaltung heute', 'Kündbar ab', 'Kosten heute',
  'Zusatzleistungen', 'Zukäufe 24 Monate', 'Pilot', 'Wahrscheinlichkeit (1–5)', 'Nennung ggü. Investoren',
  'Anmerkungen', 'Rohdaten (JSON)'
];
const KOPF_STANDORTE = ['Eingegangen', 'Ref-ID', 'Unternehmen', 'PLZ', 'PLZ-Region', 'Ort', 'Einheiten', 'Leistung', 'Nutzung', 'Frühester Start'];

const TEXT = {
  entscheider: { ja: 'Ja, allein', mit: 'Ja, gemeinsam', nein: 'Nein, bereitet vor' },
  preis: { passt: 'Passt', eher_hoch: 'Eher hoch', zu_hoch: 'Zu hoch', weiss_nicht: 'Kann ich nicht sagen' },
  heute: { eigen: 'Eigenverwaltung', extern: 'Extern', gemischt: 'Teils, teils' },
  leistung: { hv: 'Hausverwaltung', sev: 'SEV' },
  nutzung: { wohnen: 'Wohnen', gewerbe: 'Gewerbe', gemischt: 'Gemischt' },
  zusatz: { energie: 'Energie', versicherung: 'Versicherung', gutachten: 'Gutachten', mieterhoehung: 'Mieterhöhungs-Management', vertrieb: 'Vertrieb' },
  pilot: { ja: 'Ja', vielleicht: 'Vielleicht', nein: 'Nein' },
  nennung: { namentlich: 'Namentlich', anonym: 'Anonymisiert', nein: 'Nein' },
  start: { sofort: 'Ab sofort', spaeter: 'Später', offen: 'Noch offen' }
};

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.website) return antwort({ ok: true }); // Honeypot: Bots füllen das versteckte Feld aus
    if (!d.absender || !d.absender.email || !d.erklaerungen || !d.erklaerungen.unverbindlich) {
      return antwort({ ok: false, fehler: 'unvollständig' });
    }
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const lois = blatt(ss, 'LOIs', KOPF_LOIS);
    const orte = blatt(ss, 'Standorte', KOPF_STANDORTE);

    const a = d.absender, hv = d.leistungen.hausverwaltung, sev = d.leistungen.sev, z = d.zeitpunkt, x = d.ausblick;
    const eingang = new Date(d.eingegangen || Date.now());
    const start = startText(z.start);
    const gesamt = (hv ? hv.einheiten || 0 : 0) + (sev ? sev.einheiten || 0 : 0);

    lois.appendRow([
      eingang, d.ref_id || '', a.firma, a.typ, a.name, a.position, TEXT.entscheider[a.entscheider] || a.entscheider, a.email, a.telefon || '',
      hv ? hv.einheiten : '', hv ? hv.objekte || '' : '', hv ? TEXT.preis[hv.preis_feedback] || '' : '',
      sev ? sev.einheiten : '', sev ? sev.wegs || '' : '', sev ? TEXT.preis[sev.preis_feedback] || '' : '',
      gesamt, (d.standorte || []).map(ortText).join('; '), start, TEXT.heute[z.verwaltung_heute] || '', z.kuendbar_ab || '', z.kosten_heute || '',
      (x.zusatzleistungen || []).map(k => TEXT.zusatz[k] || k).join(', '), x.zukaeufe_24m == null ? '' : x.zukaeufe_24m,
      TEXT.pilot[x.pilot] || '', x.wahrscheinlichkeit || '', TEXT.nennung[d.nennung_investoren] || '',
      x.anmerkungen || '', JSON.stringify(d)
    ]);
    (d.standorte || []).forEach(s => orte.appendRow([
      eingang, d.ref_id || '', a.firma, s.plz || '', s.plz ? 'PLZ ' + String(s.plz).slice(0, 2) + 'xxx' : '', s.ort || '',
      s.einheiten || '', TEXT.leistung[s.leistung] || s.leistung, TEXT.nutzung[s.nutzung] || s.nutzung, start
    ]));

    if (BESTAETIGUNG_SENDEN) bestaetigung(d, gesamt, start);
    MailApp.sendEmail({
      to: BENACHRICHTIGUNG,
      subject: `Neues LOI: ${a.firma} – ${gesamt} Einheiten`,
      htmlBody: `<p><b>${esc(a.firma)}</b> (${esc(a.typ)}), ${esc(a.name)}, ${esc(a.position)}</p>
        <p>Hausverwaltung: ${hv ? hv.einheiten : 0} · SEV: ${sev ? sev.einheiten : 0} · Start: ${esc(start)}</p>
        <p>Standorte: ${esc((d.standorte || []).map(ortText).join('; '))}</p>
        <p><a href="${ss.getUrl()}">Zur Übersicht im Google Sheet</a></p>`
    });
    return antwort({ ok: true });
  } catch (err) {
    console.error(err);
    return antwort({ ok: false, fehler: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function bestaetigung(d, gesamt, start) {
  const a = d.absender, hv = d.leistungen.hausverwaltung, sev = d.leistungen.sev;
  const datum = Utilities.formatDate(new Date(d.eingegangen || Date.now()), 'Europe/Berlin', 'dd.MM.yyyy');
  const zeilen = [
    ['Unternehmen', `${a.firma} (${a.typ})`],
    ['Erklärt durch', `${a.name}, ${a.position}`],
    hv && ['Hausverwaltung', `${hv.einheiten} Einheiten`],
    sev && ['SEV-Verwaltung', `${sev.einheiten} Wohnungen`],
    ['Standorte', (d.standorte || []).map(ortText).join('; ')],
    ['Frühester Start', start],
    ['Datum', datum]
  ].filter(Boolean);
  const tabelle = zeilen.map(([k, v]) => `<tr><td style="color:#646a80;padding:4px 18px 4px 0">${esc(k)}</td><td style="font-weight:600;padding:4px 0">${esc(v)}</td></tr>`).join('');
  const pdfHtml = `<html><body style="font-family:Helvetica,Arial,sans-serif;color:#0b1230;padding:40px">
    <div style="font-size:12px;letter-spacing:1px;color:#646a80">CQ PROPERTY MANAGEMENT GMBH</div>
    <h1 style="font-size:24px;margin:8px 0 24px">Unverbindliche Absichtserklärung</h1>
    <table style="font-size:13px;border-collapse:collapse">${tabelle}</table>
    <p style="font-size:12px;color:#646a80;margin-top:28px;line-height:1.5">Diese Absichtserklärung dient der Marktsondierung. Sie ist kein Angebot und keine Beauftragung und begründet
    für keine Seite eine rechtliche Verpflichtung. Genannte Preise (Hausverwaltung ca. 29 €, SEV-Verwaltung 35–55 € brutto je Einheit und Monat) sind Richtwerte.
    Ein Vertrag kommt erst mit einem gesonderten, beiderseits unterschriebenen Verwaltervertrag zustande.</p>
    <p style="font-size:13px;margin-top:28px">Jan-Moritz Becker<br><span style="color:#646a80">Gründer, Cashflow Quartier</span></p>
    <p style="font-size:11px;color:#646a80;margin-top:40px">CQ Property Management GmbH · Alte Freiheit 16–18 · 42103 Wuppertal · kontakt@cashflowquartier.com</p>
    </body></html>`;
  const pdf = Utilities.newBlob(pdfHtml, 'text/html', 'LOI.html').getAs('application/pdf')
    .setName(`Absichtserklaerung_CQPM_${a.firma.replace(/[^\wäöüÄÖÜß-]+/g, '_')}.pdf`);
  const anrede = a.name ? `Hallo ${a.name},` : 'Hallo,';
  MailApp.sendEmail({
    to: a.email,
    replyTo: BENACHRICHTIGUNG,
    name: ABSENDER_NAME,
    subject: 'Deine unverbindliche Absichtserklärung an CQ Property Management',
    htmlBody: `<p>${esc(anrede)}</p>
      <p>vielen Dank für deine unverbindliche Absichtserklärung über ${gesamt} Einheiten. Im Anhang findest du deine Angaben als PDF.</p>
      <p>Wir werten gerade aus, in welchen Regionen und in welchem Umfang wir mit der Verwaltung starten. Sobald es für deinen Bestand konkret wird, melde ich mich persönlich bei dir.</p>
      <p>Viele Grüße<br>Jan-Moritz Becker<br>Gründer, Cashflow Quartier</p>
      <p style="font-size:12px;color:#646a80">CQ Property Management GmbH · Alte Freiheit 16–18 · 42103 Wuppertal</p>`,
    attachments: [pdf]
  });
}

function blatt(ss, name, kopf) {
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(kopf);
    sh.getRange(1, 1, 1, kopf.length).setFontWeight('bold').setBackground('#0b1230').setFontColor('#ffffff');
    sh.setFrozenRows(1);
  }
  return sh;
}
function startText(s) { return TEXT.start[s] || String(s || '').replace(/(\d+)-Q(\d)/, 'Q$2 $1'); }
function ortText(s) { return [s.plz, s.ort].filter(Boolean).join(' ') + (s.einheiten ? ` (${s.einheiten} ${TEXT.leistung[s.leistung] || ''})` : ''); }
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function antwort(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

/** Einmal im Editor ausführen: legt beide Blätter mit Kopfzeile an. */
function einrichten() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  blatt(ss, 'LOIs', KOPF_LOIS);
  blatt(ss, 'Standorte', KOPF_STANDORTE);
}
