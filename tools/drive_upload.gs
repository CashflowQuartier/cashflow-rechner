/**
 * Cashflow Quartier – Upload-Briefkasten für den Teaser-Generator.
 *
 * Nimmt Dateien (PDF, JPG) per HTTPS-POST entgegen und legt sie in einem Google-Drive-Ordner ab.
 * Einrichtung: siehe tools/DRIVE_UPLOAD.md. Das TOKEN unten durch eine eigene zufällige Zeichenfolge ersetzen
 * und denselben Wert in der Claude-Umgebung als CFQ_DRIVE_UPLOAD_TOKEN hinterlegen.
 */
const TOKEN = 'HIER-EIGENES-GEHEIMES-TOKEN-EINTRAGEN';
// Nur in diesen Ordnern (inkl. Unterordnern) darf abgelegt werden – Projektordner-IDs eintragen.
const ERLAUBTE_WURZELN = ['1v6qlIBdmANF-Of7ucvxxv8nZFyd4LmNM'];

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.token !== TOKEN) return antwort({ ok: false, fehler: 'token' });
    const ordner = DriveApp.getFolderById(d.folderId);
    if (!liegtUnter(ordner, ERLAUBTE_WURZELN)) return antwort({ ok: false, fehler: 'ordner nicht erlaubt' });
    const bestehend = ordner.getFilesByName(d.name);
    while (bestehend.hasNext()) bestehend.next().setTrashed(true); // gleiche Datei ersetzen statt duplizieren
    const blob = Utilities.newBlob(Utilities.base64Decode(d.data), d.mimeType, d.name);
    const datei = ordner.createFile(blob);
    return antwort({ ok: true, id: datei.getId(), url: datei.getUrl() });
  } catch (err) {
    return antwort({ ok: false, fehler: String(err) });
  }
}

function liegtUnter(ordner, wurzeln) {
  let aktuell = ordner;
  for (let i = 0; i < 20 && aktuell; i++) {
    if (wurzeln.indexOf(aktuell.getId()) >= 0) return true;
    const eltern = aktuell.getParents();
    aktuell = eltern.hasNext() ? eltern.next() : null;
  }
  return false;
}

function antwort(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
