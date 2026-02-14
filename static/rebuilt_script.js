// you need this to make sure the scoring locations arent null
function safeParseInt(v) {
    const n = parseInt(v, 10);
    return isNaN(n) ? 0 : n;
}

// ---------- accuracy sliders you HAVE TO SYNC hidden WTForms fields----------
function initSlider(sliderId, hiddenId, labelId) {
    const slider = document.getElementById(sliderId);
    const hidden = document.getElementById(hiddenId);
    const label = document.getElementById(labelId);
    if (!slider || !hidden || !label) return;

    const start = (hidden.value !== '' ? safeParseInt(hidden.value) : 0);
    const safe = Math.max(0, Math.min(100, start));
    slider.value = safe;
    hidden.value = safe;
    label.textContent = safe + '%';

    slider.addEventListener('input', function () {
        hidden.value = this.value;
        label.textContent = this.value + '%';
    });
}
initSlider('autoAccuracySlider', 'autoShotAccuracy', 'autoAccuracyValue');
initSlider('teleopAccuracySlider', 'teleopShotAccuracy', 'teleopAccuracyValue');

document.querySelectorAll('.stepper').forEach(stepper => {
    const targetName = stepper.dataset.target;
    const input = document.getElementById(targetName);
    if (!input) return;

    stepper.querySelectorAll('.stepBtn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const delta = safeParseInt(this.dataset.delta);
            const cur = safeParseInt(input.value);
            input.value = Math.max(0, cur + delta);
        });
    });
});



document.querySelectorAll('.miniStepper').forEach(stepper => {
    const targetName = stepper.dataset.target;
    const input = document.getElementById(targetName);
    if (!input) return;

    stepper.querySelectorAll('.miniStepBtn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const delta = safeParseInt(this.dataset.delta);
            const cur = safeParseInt(input.value);
            input.value = Math.max(0, cur + delta);
        });
    });
});

(function initClimb() {
    const climbInput = document.getElementById('climb');
    if (!climbInput) return;

    document.querySelectorAll('.climbGridBtn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelectorAll('.climbGridBtn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            climbInput.value = this.dataset.level;
            stopClimbTimer();
        });
    });
})();

let timerInterval = null;
let timerStartTime = null;
const climbStartBtn = document.getElementById('climbStartBtn');
const climbTimer = document.getElementById('climbTimer');
const climbFailedCheckbox = document.querySelector('input[name="climbFailed"]');

function updateClimbTimer() {
    const elapsed = (Date.now() - timerStartTime) / 1000;
    climbTimer.textContent = elapsed.toFixed(1) + 's';
}

function stopClimbTimer() {
    if (timerInterval !== null) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    if (climbStartBtn) {
        climbStartBtn.textContent = 'Start Timer';
        climbStartBtn.classList.remove('active');
    }
}

if (climbStartBtn) { 
    climbStartBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (timerInterval === null) {
            timerStartTime = Date.now();
            timerInterval = setInterval(updateClimbTimer, 100);
            climbStartBtn.textContent = 'Stop Timer';
            climbStartBtn.classList.add('active');
        } else {
            stopClimbTimer();
        }
    });
}

if (climbFailedCheckbox) {
    climbFailedCheckbox.addEventListener('change', function () {
        if (this.checked) {
            stopClimbTimer();
            if (climbTimer) climbTimer.textContent = '0.0s';
            document.querySelectorAll('.climbGridBtn').forEach(b => b.classList.remove('selected'));
            const climbInput = document.getElementById('climb');
            if (climbInput) climbInput.value = 'none';
        }
    });
}

// ---------- multi-click + filtering of incorrect clicks ----------
(function initFieldMap() {
    const img = document.getElementById('rebuiltFieldImg');
    const overlay = document.getElementById('fieldMapOverlay');
    const hidden = document.getElementById('teleopScoreLocation');
    const countEl = document.getElementById('fieldMapCount');
    const lastEl = document.getElementById('fieldMapLas/;d[t');
    const undoBtn = document.getElementById('fieldUndoBtn');
    const clearBtn = document.getElementById('fieldClearBtn');
    if (!img || !overlay || !hidden || !countEl || !lastEl || !undoBtn || !clearBtn) return;

    // store clicks as [{label:'red_back_right', x:0.91, y:0.62}]
    const clicks = [];

    // right-of-trench for red, left-of-trench for blue
    // ALL OTHER VALUES/CLICKS ARE IGNORED
    const BLUE_BAND_MAX_X = 0.18;  // left band
    const RED_BAND_MIN_X = 0.82;  // right band

    function classifyAllowed(xNorm, yNorm) {
        if (xNorm <= BLUE_BAND_MAX_X) {
            const fb = (yNorm < 0.5) ? 'front' : 'back';
            return { label: `blue_${fb}_left`, dotClass: 'fieldMapDot--blue' };
        }
        if (xNorm >= RED_BAND_MIN_X) {
            const fb = (yNorm < 0.5) ? 'front' : 'back';
            return { label: `red_${fb}_right`, dotClass: 'fieldMapDot--red' };
        }
        return null;
    }

    function renderDots() { //this is how you show all dots on the map at once, instead of only 1 at a time
        overlay.innerHTML = '';
        for (const c of clicks) {
            const dot = document.createElement('div');
            dot.className = 'fieldMapDot ' + (c.dotClass || '');
            dot.style.left = (c.x * 100).toFixed(2) + '%';
            dot.style.top = (c.y * 100).toFixed(2) + '%';
            overlay.appendChild(dot);
        }
    }

    function syncHidden() {
        const labels = clicks.map(c => c.label);
        hidden.value = labels.length ? labels.join(',') : 'none';
        countEl.textContent = String(labels.length);
        lastEl.textContent = labels.length ? labels[labels.length - 1] : 'none';
    }

    function addClick(xNorm, yNorm) {
        const cls = classifyAllowed(xNorm, yNorm);
        if (!cls) return;

        clicks.push({ label: cls.label, dotClass: cls.dotClass, x: xNorm, y: yNorm });
        renderDots();
        syncHidden();
        console.log("aaah", clicks);
    }

    function getNormalizedFromEvent(e) {
        const rect = img.getBoundingClientRect();
        const clientX = (e.clientX !== undefined) ? e.clientX : (e.touches && e.touches[0] ? e.touches[0].clientX : null);
        const clientY = (e.clientY !== undefined) ? e.clientY : (e.touches && e.touches[0] ? e.touches[0].clientY : null);
        if (clientX === null || clientY === null) return null;

        const naturalW = img.naturalWidth || rect.width;
        const naturalH = img.naturalHeight || rect.height;
        const rectRatio = rect.width / rect.height;
        const imgRatio = naturalW / naturalH;

        let drawW = rect.width;
        let drawH = rect.height;
        let offsetX = 0;
        let offsetY = 0;

        if (imgRatio > rectRatio) {
            // image is wider = letterbox top/bottom
            drawH = rect.width / imgRatio;
            offsetY = (rect.height - drawH) / 2;
        } else {
            // image is taller = letterbox left/right
            drawW = rect.height * imgRatio;
            offsetX = (rect.width - drawW) / 2;
        }

        const x = (clientX - rect.left - offsetX) / drawW;
        const y = (clientY - rect.top - offsetY) / drawH;

        if (x < 0 || x > 1 || y < 0 || y > 1) return null;

        return { xNorm: Math.min(1, Math.max(0, x)), yNorm: Math.min(1, Math.max(0, y)) };
    }

    function onPointer(e) {
        e.preventDefault();
        const norm = getNormalizedFromEvent(e);
        if (!norm) return;
        addClick(norm.xNorm, norm.yNorm);
        console.log("clicked at", norm);
    }

    img.addEventListener('pointerdown', onPointer);
    img.addEventListener('click', onPointer);

    undoBtn.addEventListener('click', function (e) { //undo last click, always keep error catching buttons (peons)
        e.preventDefault();
        if (clicks.length) {
            clicks.pop();
            renderDots();
            syncHidden();
        }
    });

    clearBtn.addEventListener('click', function (e) {
        e.preventDefault();
        clicks.length = 0;
        renderDots();
        syncHidden();
    });

    const existing = (hidden.value || '').trim();
    if (existing && existing !== 'none') {
        // can also store points, but only labels for now. probably need to change this so the map is more accurate in sheets when data is transferred
        const labels = existing.split(',').map(s => s.trim()).filter(Boolean);
        for (const label of labels) {
            // place restored dots off-screen but preserve list
            clicks.push({ label, dotClass: label.startsWith('blue_') ? 'fieldMapDot--blue' : 'fieldMapDot--red', x: -1, y: -1 });
        }
        syncHidden();
        overlay.innerHTML = '';
    } else {
        hidden.value = 'none';
        syncHidden();
    }

})();



document.addEventListener("DOMContentLoaded", () => {
  const svg = document.getElementById("heatmapSvg");
  if (!svg) return;

  window.heatClicks = window.heatClicks || []; // {x, y, t}

  window.heatmap_fr = window.heatmap_fr || {
    R1: 0, R2: 0, R3: 0, R4: 0,
    B1: 0, B2: 0, B3: 0, B4: 0
  };

  function svgClientToViewBox(svgEl, clientX, clientY) {
    const pt = svgEl.createSVGPoint();
    pt.x = clientX;
    pt.y = clientY;
    const ctm = svgEl.getScreenCTM();
    if (!ctm) return { x: 0, y: 0 };
    return pt.matrixTransform(ctm.inverse());
  }

  function sortIntoFreqs(coordinate) {
    if (coordinate.x <= 200) {
      if (coordinate.y <= 100) window.heatmap_fr.R1 += 1;
      else if (coordinate.y <= 200) window.heatmap_fr.R2 += 1;
      else if (coordinate.y <= 300) window.heatmap_fr.R3 += 1;
      else if (coordinate.y <= 400) window.heatmap_fr.R4 += 1;
    } else if (coordinate.x >= 600) {
      if (coordinate.y <= 100) window.heatmap_fr.B1 += 1;
      else if (coordinate.y <= 200) window.heatmap_fr.B2 += 1;
      else if (coordinate.y <= 300) window.heatmap_fr.B3 += 1;
      else if (coordinate.y <= 400) window.heatmap_fr.B4 += 1;
    }

    const freqEl = document.getElementById("heatmap_frequencies");
    if (freqEl) freqEl.value = JSON.stringify(window.heatmap_fr);
  }

  clicksActual = []

  svg.addEventListener("click", (ev) => {
    const p = svgClientToViewBox(svg, ev.clientX, ev.clientY);
    const x = Math.round(p.x);
    const y = Math.round(p.y);

    const t = Math.floor(Date.now() / 1000);

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", p.x);
    circle.setAttribute("cy", p.y);
    circle.setAttribute("r", 25);
    circle.setAttribute("fill", "url(#grad1)");
    circle.setAttribute("pointer-events", "none");
    if(p.x>30 && p.x<770 && p.y>30 && p.y<370 && (p.x<=200 || p.x>=600)) {
        svg.appendChild(circle);
        window.heatClicks.push({ x, y, t });
        const posEl = document.getElementById("total_positions");
        if (posEl) posEl.value = JSON.stringify(window.heatClicks);
        sortIntoFreqs({ x, y });
    }
    clicksActual.push({ x, y, t });
    console.log(clicksActual);
  });
});




function removeLastClick(){
    const svg = document.getElementById("heatmapSvg");
    if (!svg) return;
    const circles = svg.querySelectorAll("circle");
    circles[circles.length - 1].remove();
    item=window.heatClicks.pop();
    const coordinate = item;

    if (coordinate.x <= 200) {
      if (coordinate.y <= 100) window.heatmap_fr.R1 -= 1;
      else if (coordinate.y <= 200) window.heatmap_fr.R2 -= 1;
      else if (coordinate.y <= 300) window.heatmap_fr.R3 -= 1;
      else if (coordinate.y <= 400) window.heatmap_fr.R4 -= 1;
    } else if (coordinate.x >= 600) {
      if (coordinate.y <= 100) window.heatmap_fr.B1 += 1;
      else if (coordinate.y <= 200) window.heatmap_fr.B2 += 1;
      else if (coordinate.y <= 300) window.heatmap_fr.B3 += 1;
      else if (coordinate.y <= 400) window.heatmap_fr.B4 += 1;
    }

    const freqEl = document.getElementById("heatmap_frequencies");
    if (freqEl) freqEl.value = JSON.stringify(window.heatmap_fr);

    const posEl = document.getElementById('total_positions');
    if (posEl) posEl.value = JSON.stringify(window.heatClicks);
}

