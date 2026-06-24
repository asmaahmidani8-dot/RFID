/**
 * etiquette.js — Étiquette de chariot style GE (réutilisable)
 * GE Healthcare Buc | Ligne Pristina | RFID
 *
 * Code-barres CODE 128 HORIZONTAL = le NUMÉRO DE JOB (of_number), comme la vraie
 * étiquette GE (Brilliant Factory BUC). Reste = mise en page style GE.
 * Données (d) : org, of_number, item_code, item_desc, operation_code, qty_totale
 *
 * Usage :
 *   document.getElementById('cible').innerHTML = buildEtiquetteHtml(d);
 *   drawEtiquetteQR(d);   // no-op : le code-barres se charge via l'<img src>
 */

function buildEtiquetteHtml(d) {
    const item = d.item_code || '—';
    const op   = (d.operation_code || '').toString().toUpperCase().replace('OP', '');
    const job  = String(d.of_number || '');
    const ligne = `<span style="white-space:nowrap;">PRISTINA</span> <strong>${item}</strong>`;

    function row(k, v) {
        return `<div style="display:flex;padding:6px 0;border-bottom:1px solid #f1f5f9;">
                  <div style="width:120px;color:#64748b;font-size:.78rem;font-weight:600;text-transform:uppercase;">${k}</div>
                  <div style="flex:1;font-size:.92rem;font-weight:700;color:#0f172a;">${v}</div>
                </div>`;
    }

    // Un code-barres Code 128 réutilisable (image générée côté serveur)
    function barcode(text, h) {
        return `<img src="/api/barcode?text=${encodeURIComponent(text)}"
                     alt="${text}" style="display:block;height:${h}px;width:100%;
                     object-fit:contain;image-rendering:pixelated;"/>`;
    }

    return `
    <div class="etiquette-ge" style="background:white;border:1px solid #cbd5e1;border-radius:10px;
         max-width:640px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;overflow:hidden;
         box-shadow:0 4px 16px rgba(0,0,0,.1);">

      <!-- Bandeau GE -->
      <div style="background:#003087;color:white;padding:9px 16px;display:flex;
           justify-content:space-between;align-items:center;">
        <div style="font-weight:800;letter-spacing:.5px;font-size:.95rem;">ÉTIQUETTE CHARIOT</div>
        <div style="font-size:.7rem;opacity:.85;">${new Date().toLocaleDateString('fr-FR')}</div>
      </div>

      <!-- Corps : infos seulement -->
      <div style="padding:14px 18px;">
        ${row('Org', d.org || 'BXD')}
        ${row('Line', ligne)}
        ${row('Item', item)}
        ${row('Description', d.item_desc || '—')}
        ${row('Opération', 'OP' + op)}
      </div>

      <!-- Pied : grand code-barres du JOB + N° (gauche) + quantités (droite) -->
      <div style="display:flex;justify-content:space-between;align-items:flex-end;
           padding:14px 18px;background:#f8fafc;border-top:2px solid #003087;gap:18px;">
        <div style="flex:1;min-width:0;">
          <div style="background:white;padding:4px 0;max-width:380px;">
            ${barcode(job, 50)}
          </div>
          <div style="font-size:1.9rem;font-weight:900;color:#003087;letter-spacing:1px;margin-top:4px;">${job || '—'}</div>
        </div>
        <div style="text-align:right;font-size:.9rem;white-space:nowrap;">
          <div style="margin-bottom:5px;"><span style="color:#64748b;">Scheduled Qty</span>
              &nbsp;<strong>${d.qty_totale || 1}</strong></div>
          <div><span style="color:#64748b;">Available Qty</span>
              &nbsp;<strong style="color:#198754;">${d.qty_totale || 1}</strong></div>
        </div>
      </div>
    </div>`;
}

// Le code-barres est généré côté SERVEUR (l'<img> pointe vers /api/barcode) → rien à faire ici.
function drawEtiquetteQR(d) { /* no-op : le code-barres se charge tout seul via l'<img src> */ }
