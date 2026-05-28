/**
 * scan.js — Logique scan QR code + assignation OF
 * GE Healthcare Buc RFID
 */

let scanner1 = null;
let scanner2 = null;
let currentChariot  = null;
let currentChariot2 = null;
let jobsData = {};  // { item_code: [of_number, ...] }

// ── Démarrer le scanner ────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    demarrerScanner1();
});

function demarrerScanner1() {
    scanner1 = new Html5Qrcode("qr-reader");
    scanner1.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScan1,
        (err) => {}
    ).then(() => {
        setStatus("Caméra active — pointez le QR code du chariot", "info");
    }).catch(err => {
        setStatus("Erreur caméra : " + err, "error");
    });
}

function onScan1(qrContent) {
    scanner1.stop().then(() => {
        setStatus("QR scanné : " + qrContent, "success");
        envoyerScan(qrContent);
    });
}

// ── Envoyer le scan au serveur ─────────────────────────────
function envoyerScan(qrContent) {
    fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qr_content: qrContent })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            setStatus("❌ " + data.error, "error");
            // Relancer le scanner après 2s
            setTimeout(() => {
                if (data.action === "erreur_groupe") {
                    demarrerScanner1();
                } else {
                    demarrerScanner1();
                }
            }, 2500);
            return;
        }

        if (data.action === "scan_groupe_2") {
            // Type B → attendre 2ème scan
            afficherAttenteGroupe(data);

        } else if (data.action === "groupe_forme") {
            // Groupe formé → afficher les OFs
            currentChariot  = data.chariot1;
            currentChariot2 = data.chariot2;
            afficherJobs(data.chariot1, data.chariot2, data.jobs);

        } else if (data.action === "assigner") {
            // Type A/C/D → afficher les OFs
            currentChariot  = data.chariot;
            currentChariot2 = null;
            afficherJobs(data.chariot, null, data.jobs);
        }
    })
    .catch(err => {
        setStatus("Erreur réseau : " + err, "error");
    });
}

// ── Attente 2ème scan (groupe Type B) ─────────────────────
function afficherAttenteGroupe(data) {
    document.getElementById("zone-scan").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.remove("d-none");
    document.getElementById("msg-scan1").textContent = data.message;

    scanner2 = new Html5Qrcode("qr-reader-2");
    scanner2.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScan2,
        (err) => {}
    );
}

function onScan2(qrContent) {
    scanner2.stop().then(() => {
        envoyerScan(qrContent);
        document.getElementById("zone-groupe-2").classList.add("d-none");
    });
}

// ── Afficher les OFs compatibles ───────────────────────────
function afficherJobs(chariot, chariot2, jobs) {
    document.getElementById("zone-scan").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.add("d-none");
    document.getElementById("zone-jobs").classList.remove("d-none");

    // Info chariot
    const infoCard = document.getElementById("chariot-info-card");
    let groupeHtml = chariot2
        ? `<span class="ms-2 badge bg-light text-dark">+ ${chariot2.chariot_id}</span>`
        : "";
    infoCard.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <div class="d-flex align-items-center gap-2 mb-1">
                    <span class="badge bg-light text-dark fw-bold">Type ${chariot.type_chariot}</span>
                    <strong>${chariot.chariot_id}</strong>${groupeHtml}
                </div>
                <div style="font-size:13px; opacity:0.85">${chariot.nom || ''}</div>
            </div>
            <div class="text-end">
                <div style="font-size:13px; opacity:0.85">Opération</div>
                <div style="font-size:1.4rem; font-weight:800">OP${chariot.operation_code}</div>
            </div>
        </div>
    `;

    if (jobs.length === 0) {
        document.getElementById("jobs-container").innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox" style="font-size:2rem; color:#ccc"></i>
                <p class="mt-2 text-muted">Aucun OF Released compatible avec ce chariot</p>
            </div>`;
        return;
    }

    // Grouper par assembly (item_code)
    const grouped = {};
    jobs.forEach(j => {
        const key = j.item_code;
        if (!grouped[key]) grouped[key] = { name: j.assembly_name || j.item_desc, jobs: [] };
        grouped[key].jobs.push(j);
    });

    jobsData = {};
    let html = "";

    Object.entries(grouped).forEach(([item_code, group]) => {
        jobsData[item_code] = null;
        html += `
        <div class="assembly-group">
            <div class="assembly-title">
                <i class="bi bi-box-seam"></i>
                ${group.name} <span class="text-muted fw-normal">(${item_code})</span>
                ${group.jobs.length === 1 ? '<span class="badge bg-success ms-2">Auto</span>' : ''}
            </div>
            <div class="job-options-list" data-item="${item_code}">`;

        group.jobs.forEach((j, idx) => {
            const auto = group.jobs.length === 1;
            html += `
                <div class="job-option ${auto ? 'selected' : ''}"
                     onclick="selectionnerJob(this, '${item_code}', '${j.of_number}', '${j.operation_code}')">
                    <input type="radio" name="job_${item_code}" value="${j.of_number}" ${auto ? 'checked' : ''}>
                    <div class="flex-grow-1">
                        <div class="job-of-number">${j.of_number}</div>
                        <div class="job-meta">${j.item_desc || ''}</div>
                        <div class="job-date"><i class="bi bi-calendar3 me-1"></i>${j.date_besoin || '—'}</div>
                    </div>
                    <div class="text-end">
                        <div style="font-size:11px; color:#6b7280">Qté</div>
                        <div style="font-weight:700">${j.qty_totale || 0}</div>
                    </div>
                </div>`;

            // Auto-sélection si 1 seul OF
            if (auto) {
                jobsData[item_code] = { of_number: j.of_number, op_code: j.operation_code };
            }
        });

        html += `</div></div>`;
    });

    document.getElementById("jobs-container").innerHTML = html;
    mettreAJourBouton();
}

// ── Sélectionner un OF ─────────────────────────────────────
function selectionnerJob(el, item_code, of_number, op_code) {
    // Désélectionner les autres dans ce groupe
    el.closest(".job-options-list").querySelectorAll(".job-option").forEach(o => {
        o.classList.remove("selected");
        o.querySelector("input").checked = false;
    });
    el.classList.add("selected");
    el.querySelector("input").checked = true;
    jobsData[item_code] = { of_number, op_code };
    mettreAJourBouton();
}

function mettreAJourBouton() {
    const allSelected = Object.values(jobsData).every(v => v !== null);
    const btn = document.getElementById("btn-assigner");
    if (allSelected && Object.keys(jobsData).length > 0) {
        btn.style.display = "flex";
        btn.style.alignItems = "center";
        btn.style.justifyContent = "center";
    } else {
        btn.style.display = "none";
    }
}

// ── Confirmer l'assignation ────────────────────────────────
function confirmerAssignation() {
    const selections = Object.entries(jobsData).map(([item_code, sel]) => ({
        item_code,
        of_number: sel.of_number,
        op_code:   sel.op_code
    }));

    const payload = {
        chariot_id:  currentChariot.chariot_id,
        chariot2_id: currentChariot2 ? currentChariot2.chariot_id : null,
        selections
    };

    fetch("/api/mission/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            document.getElementById("zone-jobs").classList.add("d-none");
            document.getElementById("zone-succes").classList.remove("d-none");
            const nb = selections.length;
            document.getElementById("succes-msg").textContent =
                `${nb} OF(s) assigné(s) au chariot ${currentChariot.chariot_id}. Mission #${data.mission_id} créée.`;
        } else {
            alert("Erreur : " + data.error);
        }
    })
    .catch(err => alert("Erreur réseau : " + err));
}

// ── Status display ─────────────────────────────────────────
function setStatus(msg, type) {
    const el = document.getElementById("scan-status");
    if (!el) return;
    const icons = { info: "bi-camera", success: "bi-check-circle", error: "bi-exclamation-triangle" };
    const colors = { info: "#374151", success: "#065f46", error: "#991b1b" };
    el.innerHTML = `<i class="bi ${icons[type] || 'bi-info-circle'} me-2"></i>${msg}`;
    el.style.color = colors[type] || "#374151";
}
