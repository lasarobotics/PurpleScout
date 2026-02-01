// you need this to make sure the scoring locations arent null
function safeParseInt(v) {
    const n = parseInt(v, 10);
    return isNaN(n) ? 0 : n;
}

// ---------- accuracy sliders you HAVE TO SYNC hidden WTForms fields (VERY IMPORTANT, WILL BREAK APP W/O)----------
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

// ---------- increment for shooting esti with error catching (-1) ----------
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

// ---------- i removed addbutton, fixed the double counting fouls erorr ----------
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

// ---------- climb grid (from samarth) ----------
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

// ----------  timer for climb, can extrapolate to overall timer etc. (from samarth) ----------
let timerInterval = null;
let timerStartTime = null;
const climbStartBtn = document.getElementById('climbStartBtn');
const climbTimer = document.getElementById('climbTimer');
const climbFailedCheckbox = document.querySelector('input[name="climbFailed"]');

function updateClimbTimer() {
    const elapsed = (Date.now() - timerStartTime) / 1000;
    climbTimer.textContent = elapsed.toFixed(1) + 's';
}

function stopClimbTimer() { //from samarth
    if (timerInterval !== null) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    if (climbStartBtn) {
        climbStartBtn.textContent = 'Start Timer';
        climbStartBtn.classList.remove('active');
    }
}

if (climbStartBtn) { //from samarth
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

if (climbFailedCheckbox) { //from samarth
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
    const lastEl = document.getElementById('fieldMapLast');
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
        // ignore everything except trench-separated scoring bands -> const value, can change later if needed
        if (xNorm <= BLUE_BAND_MAX_X) {
            // blue side (left band), i split by front/back via vertical position
            const fb = (yNorm < 0.5) ? 'front' : 'back';
            return { label: `blue_${fb}_left`, dotClass: 'fieldMapDot--blue' };
        }
        if (xNorm >= RED_BAND_MIN_X) {
            // red side (right band), const value baseed on the 2026-field.png
            const fb = (yNorm < 0.5) ? 'front' : 'back';
            return { label: `red_${fb}_right`, dotClass: 'fieldMapDot--red' };
        }
        return null; // ignore wrong values
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
        if (!cls) return; // ignore invalid click

        clicks.push({ label: cls.label, dotClass: cls.dotClass, x: xNorm, y: yNorm });
        renderDots();
        syncHidden();
    }

    function getNormalizedFromEvent(e) {
        const rect = img.getBoundingClientRect();
        const clientX = (e.clientX !== undefined) ? e.clientX : (e.touches && e.touches[0] ? e.touches[0].clientX : null);
        const clientY = (e.clientY !== undefined) ? e.clientY : (e.touches && e.touches[0] ? e.touches[0].clientY : null);
        if (clientX === null || clientY === null) return null;

        // correct by computing the actual rendered image box within the element, extraplote size to all comps
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

        // if click is in the letterboxed area, ignore
        if (x < 0 || x > 1 || y < 0 || y > 1) return null;

        return { xNorm: Math.min(1, Math.max(0, x)), yNorm: Math.min(1, Math.max(0, y)) };
    }

    function onPointer(e) {
        e.preventDefault();
        const norm = getNormalizedFromEvent(e);
        if (!norm) return;
        addClick(norm.xNorm, norm.yNorm);
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

    // initialize from existing value (if any)
    const existing = (hidden.value || '').trim();
    if (existing && existing !== 'none') {
        // only restore labels, not positions
        // can also store points, but only labels for now. probably need to change this so the map is more accurate in sheets when data is transferred
        const labels = existing.split(',').map(s => s.trim()).filter(Boolean);
        for (const label of labels) {
            // place restored dots off-screen but preserve list
            clicks.push({ label, dotClass: label.startsWith('blue_') ? 'fieldMapDot--blue' : 'fieldMapDot--red', x: -1, y: -1 });
        }
        // just sync hidden/count/last -> not actually render dots since we dont have positions. this is a limitation of only storing labels but can be changed. simplified bc i wanted to finish quickly.
        syncHidden();
        overlay.innerHTML = '';
    } else {
        hidden.value = 'none';
        syncHidden();
    }

})();

        
        
const heatClicks = []; // {x, y, t}

function svgClientToViewBox(svgEl, clientX, clientY) {
  const pt = svgEl.createSVGPoint();
  pt.x = clientX;
  pt.y = clientY;
  const ctm = svgEl.getScreenCTM();
  if (!ctm) return { x: 0, y: 0 };
  const inv = ctm.inverse();
  const p = pt.matrixTransform(inv);
  return { x: p.x, y: p.y };
}

svg.addEventListener('click', function (ev) {
  const { x, y } = svgClientToViewBox(svg, ev.clientX, ev.clientY);

heatClicks.push({ x: Math.round(x), y: Math.round(y), t: Date.now()/1000 });

const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
circle.setAttribute("cx", x);
circle.setAttribute("cy", y);
circle.setAttribute("r", 25);
circle.setAttribute("fill", "url(#grad1)");
circle.setAttribute("pointer-events", "none");
svg.appendChild(circle);

document.getElementById("positions").value = JSON.stringify(heatClicks);
sortIntoFreqs({ x: Math.round(x), y: Math.round(y)});
});

 var heatmap_fr={
    R1:0,
    R2:0,
    R3:0,
    R4:0,
    B1:0,
    B2:0,
    B3:0,
    B4:0
 }
//helper method for sorting into frequencies
function sortIntoFreqs(coordinate){
    if(coordinate.y<=100 && coordinate.x<=200)
        heatmap_fr.R1+=1;
    else if(coordinate.y<=200 && coordinate.x<=200){
        heatmap_fr.R2+=1;
    }
    else if(coordinate.y<=300 && coordinate.x<=200){
        heatmap_fr.R3+=1;
    }
    else if(coordinate.y<=400 && coordinate.x<=200){
        heatmap_fr.R4+=1;
    }
    else if(coordinate.y<=100 && coordinate.x>=600){
        heatmap_fr.B1+=1;
    }
    else if(coordinate.y<=200 && coordinate.x>=600){
        heatmap_fr.B2+=1;
    }
    else if(coordinate.y<=300 && coordinate.x>=600){
        heatmap_fr.B3+=1;
    }
    else if(coordinate.y<=400 && coordinate.x>=600){
        heatmap_fr.B4+=1;
    }
    document.getElementById("heatmap_frequencies").value=JSON.stringify(heatmap_fr);
}