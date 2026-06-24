/**
 * scan.js — Logique scan QR code + assignation OF
 * GE Healthcare Buc | Ligne Pristina | RFID
 *
 * Flux :
 *  1. Scanner le QR chariot  → /api/scan  → afficher info chariot (zone-chariot)
 *  1b. (Type B) Scanner 2ème chariot
 *  2. Cliquer "CHERCHER LES JOBS" → /api/jobs (sync Oracle) → afficher OFs (zone-jobs)
 *  3. Sélectionner les OFs
 *  4. Confirmer → /api/mission/create → zone-succes
 */

let scanner1 = null;
let scanner2 = null;
let currentChariot  = null;
let currentChariot2 = null;
let jobsData = {};
let assignationEnCours = false;

// ── Démarrer le scanner au chargement ─────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    demarrerScanner1();
});

function demarrerScanner1() {
    scanner1 = new Html5Qrcode("qr-reader");
    scanner1.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScan1,
        () => {}
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

// ── Envoyer le scan au serveur ─────────────────────────────────
function envoyerScan(qrContent) {
    cacherSpinner();
    fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qr_content: qrContent })
    })
    .then(r => r.json())
    .then(data => {
        if (data.action === "mission_active") {
            afficherMissionActive(data);
            return;
        }

        if (data.error) {
            setStatus("❌ " + data.error, "error");
            setTimeout(() => demarrerScanner1(), 2500);
            return;
        }

        if (data.action === "choisir_partenaire") {
            // Type B — choisir la partie 2 dans une liste (pas de 2ème scan)
            afficherChoixPartenaire(data);
            return;
        }

        if (data.action === "scan_groupe_2") {
            // Type B — attendre 2ème scan
            afficherAttenteGroupe(data);

        } else if (data.action === "groupe_forme") {
            // Groupe formé → afficher info + bouton
            currentChariot  = data.chariot1;
            currentChariot2 = data.chariot2;
            afficherChariot(data.chariot1, data.chariot2);

        } else if (data.action === "chariot_identifie") {
            // Type A / C / D → afficher info + bouton
            currentChariot  = data.chariot;
            currentChariot2 = null;
            afficherChariot(data.chariot, null);
        }
    })
    .catch(err => {
        setStatus("Erreur réseau : " + err, "error");
    });
}

// ── Mission active — blocage rescan ───────────────────────────
function afficherMissionActive(data) {
    cacherSpinner();
    currentChariot = null;
    currentChariot2 = null;
    jobsData = {};
    document.getElementById("zone-scan").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.add("d-none");
    document.getElementById("zone-chariot").classList.add("d-none");
    document.getElementById("zone-jobs").classList.add("d-none");
    document.getElementById("zone-succes").classList.add("d-none");

    const statut = data.statut || "EN COURS";
    const couleur = statut === "EN_ATTENTE" ? "#f59e0b" : "#3b82f6";

    let zoneActive = document.getElementById("zone-mission-active");
    if (!zoneActive) {
        zoneActive = document.createElement("div");
        zoneActive.id = "zone-mission-active";
        // Conteneur de backend_test = .straxi-content (fallback robuste)
        const cont = document.querySelector(".straxi-content")
                  || document.querySelector(".ge-content")
                  || document.body;
        cont.appendChild(zoneActive);
    }

    zoneActive.classList.remove("d-none");
    zoneActive.innerHTML = `
        <div class="mx-3 mt-4">
            <div class="mission-card" style="border-left:4px solid ${couleur}">
                <div class="mission-header">
                    <div class="d-flex align-items-center gap-2">
                        <i class="bi bi-exclamation-triangle-fill" style="color:${couleur};font-size:1.3rem"></i>
                        <strong>Chariot déjà en mission active</strong>
                    </div>
                    <span class="statut-badge" style="background:${couleur};color:#fff">
                        ${statut.replace('_', ' ')}
                    </span>
                </div>
                <div class="mission-body mt-2">
                    <span class="info-chip"><i class="bi bi-hash"></i> Mission #${data.mission_id}</span>
                    <p class="mt-2 text-muted small mb-0">
                        ${data.error || "Ce chariot a une mission en cours."}
                    </p>
                </div>
            </div>
            <button class="btn-chercher mt-3 w-100" onclick="resetScan()">
                <i class="bi bi-arrow-repeat me-2"></i>Scanner un autre chariot
            </button>
        </div>`;
}

// ── ÉTAPE 1b : Attente 2ème scan (groupe Type B) ──────────────
function afficherAttenteGroupe(data) {
    document.getElementById("zone-scan").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.remove("d-none");

    // Mémoriser le 1er chariot → on ignorera un re-scan du MÊME QR
    window._scan1_id = (data.chariot && data.chariot.chariot_id) ? data.chariot.chariot_id : null;

    // Compte à rebours avant d'activer la caméra → le temps de viser le 2ème chariot
    const msgEl = document.getElementById("msg-scan1");
    const base  = data.message || "1er chariot scanné.";
    let n = 3;
    msgEl.textContent = `${base}  —  Préparez le 2ème chariot (${n})`;
    const tick = setInterval(() => {
        n--;
        if (n > 0) {
            msgEl.textContent = `${base}  —  Préparez le 2ème chariot (${n})`;
        } else {
            clearInterval(tick);
            msgEl.textContent = base;
            demarrerScanner2();
        }
    }, 1000);
}

function demarrerScanner2() {
    scanner2 = new Html5Qrcode("qr-reader-2");
    scanner2.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScan2,
        () => {}
    );
}

function onScan2(qrContent) {
    // Si on relit le MÊME chariot (partie 1) → on ignore et on continue à scanner
    const id2 = qrContent.replace("CHARIOT:", "").split("|")[0].trim();
    if (window._scan1_id && id2 === window._scan1_id) {
        setStatus("C'est le 1er chariot — visez le 2ème (partie différente)", "info");
        return;   // scanner2 reste actif
    }
    scanner2.stop().then(() => {
        document.getElementById("zone-groupe-2").classList.add("d-none");
        envoyerScan(qrContent);
    });
}

// ── ÉTAPE 1b (Type B) : CHOISIR le partenaire dans une liste ──
function afficherChoixPartenaire(data) {
    cacherSpinner();
    document.getElementById("zone-scan").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.add("d-none");

    window._chariot1     = data.chariot;
    window._partenaires  = data.partenaires || [];

    let zone = document.getElementById("zone-partenaire");
    if (!zone) {
        zone = document.createElement("div");
        zone.id = "zone-partenaire";
        (document.querySelector(".straxi-content") || document.body).appendChild(zone);
    }
    zone.classList.remove("d-none");

    let boutons;
    if (window._partenaires.length === 0) {
        boutons = `<div class="alert alert-warning">Aucun chariot partie ${data.autre_partie} LIBRE à ce feeder.</div>`;
    } else {
        boutons = window._partenaires.map((p, i) => `
            <button class="btn-chercher mb-2 w-100" style="text-align:left"
                    onclick="choisirPartenaire(${i})">
                <i class="bi bi-cart3 me-2"></i>${p.nom || p.chariot_id}
            </button>`).join("");
    }

    zone.innerHTML = `
        <div class="px-3 pt-3">
            <div class="alert-groupe">
                <i class="bi bi-check-circle-fill me-2"></i>
                <strong>1er chariot : ${data.chariot.nom || data.chariot.chariot_id}</strong>
            </div>
            <div class="scan-header mb-2 mt-3">
                <h5 class="mb-1"><i class="bi bi-people me-2"></i>Choisir la partie ${data.autre_partie}</h5>
                <p class="text-muted small mb-2">Tape le chariot partie ${data.autre_partie} présent (libres uniquement)</p>
            </div>
            ${boutons}
            <button class="btn btn-outline-secondary w-100 mt-2" onclick="annulerPartenaire()">
                <i class="bi bi-arrow-repeat me-2"></i>Annuler
            </button>
        </div>`;
}

function choisirPartenaire(i) {
    const partner = (window._partenaires || [])[i];
    if (!partner) return;
    currentChariot  = window._chariot1;
    currentChariot2 = partner;
    const zone = document.getElementById("zone-partenaire");
    if (zone) zone.classList.add("d-none");
    afficherChariot(window._chariot1, partner);
}

function annulerPartenaire() {
    const zone = document.getElementById("zone-partenaire");
    if (zone) zone.classList.add("d-none");
    resetScan();
}

// ── ÉTAPE 2 : Chariot identifié → afficher la carte + bouton ──
function afficherChariot(chariot, chariot2) {
    document.getElementById("zone-scan").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.add("d-none");
    document.getElementById("zone-chariot").classList.remove("d-none");

    document.getElementById("chariot-info-card").innerHTML =
        buildChariotCardHtml(chariot, chariot2);
}

function buildChariotCardHtml(chariot, chariot2) {
    const groupeHtml = chariot2
        ? `<span class="ms-2 badge bg-light text-dark">+ ${chariot2.chariot_id}</span>`
        : "";
    return `
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
        </div>`;
}

// ── ÉTAPE 2 → 3 : Bouton "CHERCHER LES JOBS" ──────────────────
function chercherJobs() {
    const btn = document.getElementById("btn-chercher");
    btn.disabled = true;

    afficherSpinner("Sync Oracle en cours...");

    fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            chariot_id:  currentChariot.chariot_id,
            chariot2_id: currentChariot2 ? currentChariot2.chariot_id : null
        })
    })
    .then(r => r.json())
    .then(data => {
        cacherSpinner();
        btn.disabled = false;

        if (data.action === "mission_active") {
            afficherMissionActive(data);
            return;
        }

        if (data.error) {
            alert("Erreur sync : " + data.error);
            return;
        }
        if (!data.sync_ok) {
            setStatus("⚠️ Oracle inaccessible — données en cache local", "error");
        }
        afficherJobs(currentChariot, currentChariot2, data.jobs);
    })
    .catch(err => {
        cacherSpinner();
        btn.disabled = false;
        setStatus("Erreur reseau : " + err, "error");
    });
}

// ── ÉTAPE 3 : Afficher les OFs compatibles ────────────────────
function afficherJobs(chariot, chariot2, jobs) {
    document.getElementById("zone-chariot").classList.add("d-none");
    document.getElementById("zone-jobs").classList.remove("d-none");
    cacherErreurAssignation();

    // Info chariot en haut de la zone-jobs
    document.getElementById("chariot-info-card-2").innerHTML =
        buildChariotCardHtml(chariot, chariot2);

    if (jobs.length === 0) {
        document.getElementById("jobs-container").innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox" style="font-size:2rem; color:#ccc"></i>
                <p class="mt-2 text-muted">Aucun OF Released compatible avec ce chariot</p>
            </div>`;
        document.getElementById("btn-assigner").style.display = "none";
        return;
    }

    jobsData = {};

    const nbJobs = chariot.nb_jobs || 1;

    if (nbJobs === 1) {
        // ── NB_JOBS = 1 : liste plate, WS choisit UN seul OF ──
        afficherJobsPlat(jobs);
    } else {
        // ── NB_JOBS > 1 : groupé par assembly, un OF par groupe ─
        afficherJobsGroupes(jobs);
    }

    mettreAJourBouton();
}

// Liste plate — 1 seul OF à choisir parmi tous les modèles
function afficherJobsPlat(jobs) {
    jobsData["_selection"] = null;
    let html = `
    <div class="assembly-group">
        <div class="assembly-title mb-2">
            <i class="bi bi-arrow-right-circle"></i>
            Choisir le modèle en cours d'assemblage
        </div>
        <div class="job-options-list" data-item="_selection">`;

    jobs.forEach(j => {
        html += `
            <div class="job-option"
                 onclick="selectionnerJob(this, '_selection', '${j.of_number}', '${j.operation_code}', '${j.item_code}')">
                <input type="radio" name="job__selection" value="${j.of_number}">
                <div class="flex-grow-1">
                    <div class="job-of-number">${j.of_number}</div>
                    <div class="job-meta" style="font-weight:600; color:#176782">${j.assembly_name || j.item_desc || ''}</div>
                    <div class="job-meta">${j.item_code}</div>
                    <div class="job-date"><i class="bi bi-calendar3 me-1"></i>${j.date_besoin || '—'}</div>
                </div>
                <div class="text-end">
                    <div style="font-size:11px; color:#6b7280">Qté</div>
                    <div style="font-weight:700">${j.qty_totale || 0}</div>
                </div>
            </div>`;
    });

    html += `</div></div>`;
    document.getElementById("jobs-container").innerHTML = html;
}

// Groupé par assembly — un OF par groupe (nb_jobs > 1)
function afficherJobsGroupes(jobs) {
    const grouped = {};
    jobs.forEach(j => {
        const key = j.item_code;
        if (!grouped[key]) grouped[key] = { name: j.assembly_name || j.item_desc, jobs: [] };
        grouped[key].jobs.push(j);
    });

    let html = "";
    Object.entries(grouped).forEach(([item_code, group]) => {
        jobsData[item_code] = null;
        const auto = group.jobs.length === 1;
        html += `
        <div class="assembly-group">
            <div class="assembly-title">
                <i class="bi bi-box-seam"></i>
                ${group.name}
                <span class="text-muted fw-normal">(${item_code})</span>
                ${auto ? '<span class="badge bg-success ms-2">Auto</span>' : ''}
            </div>
            <div class="job-options-list" data-item="${item_code}">`;

        group.jobs.forEach(j => {
            html += `
                <div class="job-option ${auto ? 'selected' : ''}"
                     onclick="selectionnerJob(this, '${item_code}', '${j.of_number}', '${j.operation_code}', '${j.item_code}')">
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
            if (auto) {
                jobsData[item_code] = { of_number: j.of_number, op_code: j.operation_code, item_code };
            }
        });

        html += `</div></div>`;
    });

    document.getElementById("jobs-container").innerHTML = html;
}

// ── Sélectionner un OF ────────────────────────────────────────
function selectionnerJob(el, group_key, of_number, op_code, item_code) {
    el.closest(".job-options-list").querySelectorAll(".job-option").forEach(o => {
        o.classList.remove("selected");
        o.querySelector("input").checked = false;
    });
    el.classList.add("selected");
    el.querySelector("input").checked = true;
    // item_code réel (pour nb_jobs=1, group_key="_selection")
    const real_item = item_code || group_key;
    jobsData[group_key] = { of_number, op_code, item_code: real_item };
    mettreAJourBouton();
}

function mettreAJourBouton() {
    const allSelected = Object.values(jobsData).every(v => v !== null);
    const btn = document.getElementById("btn-assigner");
    btn.style.display = (allSelected && Object.keys(jobsData).length > 0) ? "flex" : "none";
}

// ── ÉTAPE 4 : Confirmer l'assignation ─────────────────────────
function afficherErreurAssignation(message) {
    const el = document.getElementById("assign-error");
    if (!el) return;
    el.textContent = message || "Impossible de creer la mission.";
    el.classList.remove("d-none");
}

function cacherErreurAssignation() {
    const el = document.getElementById("assign-error");
    if (!el) return;
    el.textContent = "";
    el.classList.add("d-none");
}

function confirmerAssignation() {
    if (assignationEnCours) return;
    assignationEnCours = true;
    const btn = document.getElementById("btn-assigner");
    if (btn) {
        btn.disabled = true;
        btn.style.opacity = "0.65";
    }

    const selections = Object.entries(jobsData).map(([group_key, sel]) => ({
        item_code: sel.item_code || group_key,
        of_number: sel.of_number,
        op_code:   sel.op_code
    }));

    const payload = {
        chariot_id:  currentChariot.chariot_id,
        chariot2_id: currentChariot2 ? currentChariot2.chariot_id : null,
        selections
    };

    afficherSpinner("Création de la mission...");
    cacherErreurAssignation();

    fetch("/api/mission/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        cacherSpinner();
        if (data.success) {
            document.getElementById("zone-jobs").classList.add("d-none");
            document.getElementById("zone-succes").classList.remove("d-none");
            document.getElementById("succes-msg").textContent =
                `${selections.length} OF(s) assigné(s) au chariot ${currentChariot.chariot_id}. Mission #${data.mission_id} créée.`;
        } else {
            assignationEnCours = false;
            if (btn) {
                btn.disabled = false;
                btn.style.opacity = "1";
            }
            afficherErreurAssignation(data.error || "Mission non creee.");
        }
    })
    .catch(err => {
        cacherSpinner();
        assignationEnCours = false;
        if (btn) {
            btn.disabled = false;
            btn.style.opacity = "1";
        }
        afficherErreurAssignation("Erreur reseau : " + err);
    });
}

// ── Actualiser (re-sync + reload jobs) ────────────────────────
function relancerSync() {
    document.getElementById("zone-jobs").classList.add("d-none");
    document.getElementById("zone-chariot").classList.remove("d-none");
    chercherJobs();
}

// ── Helpers ───────────────────────────────────────────────────
function setStatus(msg, type) {
    const el = document.getElementById("scan-status");
    if (!el) return;
    const icons  = { info: "bi-camera", success: "bi-check-circle", error: "bi-exclamation-triangle" };
    const colors = { info: "#374151",   success: "#065f46",          error: "#991b1b" };
    el.innerHTML = `<i class="bi ${icons[type] || 'bi-info-circle'} me-2"></i>${msg}`;
    el.style.color = colors[type] || "#374151";
}

function afficherSpinner(msg) {
    document.getElementById("spinner-msg").textContent = msg || "Chargement...";
    const sp = document.getElementById("spinner");
    sp.style.display = "";          // ré-autorise l'affichage
    sp.classList.add("active");
}

function cacherSpinner() {
    const sp = document.getElementById("spinner");
    if (!sp) return;
    sp.classList.remove("active");
    sp.style.display = "none";      // force le masquage (robuste)
}

function resetScan() {
    currentChariot  = null;
    currentChariot2 = null;
    jobsData = {};
    const zoneActive = document.getElementById("zone-mission-active");
    if (zoneActive) zoneActive.classList.add("d-none");
    const zonePart = document.getElementById("zone-partenaire");
    if (zonePart) zonePart.classList.add("d-none");
    document.getElementById("zone-chariot").classList.add("d-none");
    document.getElementById("zone-jobs").classList.add("d-none");
    document.getElementById("zone-groupe-2").classList.add("d-none");
    document.getElementById("zone-scan").classList.remove("d-none");
    demarrerScanner1();
}
