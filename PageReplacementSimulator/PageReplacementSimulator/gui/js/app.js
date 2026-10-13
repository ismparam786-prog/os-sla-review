/**
 * app.js
 * -------
 * UI controller for the Page Replacement Simulator GUI.
 * Wires the input card, the LRU/Optimal result cards, the bottom
 * comparison cards and the bar charts to the algorithm functions in
 * algorithms.js, using the same validation rules as the CLI (validator.js).
 */

let selectedAlgo = "lru"; // default selection, matches the mockup (LRU highlighted)

const els = {
  refInput: document.getElementById("refString"),
  frameInput: document.getElementById("frameCount"),
  algoButtons: document.querySelectorAll(".algo-btn"),
  runBtn: document.getElementById("runBtn"),
  errorBox: document.getElementById("errorBox"),

  lruCard: document.getElementById("lruCard"),
  optCard: document.getElementById("optCard"),
  lruTableBody: document.querySelector("#lruTable tbody"),
  optTableBody: document.querySelector("#optTable tbody"),
  lruTableHead: document.querySelector("#lruTable thead tr"),
  optTableHead: document.querySelector("#optTable thead tr"),
  lruFaults: document.getElementById("lruFaults"),
  lruHitRatio: document.getElementById("lruHitRatio"),
  optFaults: document.getElementById("optFaults"),
  optHitRatio: document.getElementById("optHitRatio"),

  cmpLruFaults: document.getElementById("cmpLruFaults"),
  cmpOptFaults: document.getElementById("cmpOptFaults"),
  cmpLruHit: document.getElementById("cmpLruHit"),
  cmpOptHit: document.getElementById("cmpOptHit"),

  faultBarLru: document.getElementById("faultBarLru"),
  faultBarOpt: document.getElementById("faultBarOpt"),
  faultBarLruVal: document.getElementById("faultBarLruVal"),
  faultBarOptVal: document.getElementById("faultBarOptVal"),
  hitBarLru: document.getElementById("hitBarLru"),
  hitBarOpt: document.getElementById("hitBarOpt"),
  hitBarLruVal: document.getElementById("hitBarLruVal"),
  hitBarOptVal: document.getElementById("hitBarOptVal"),

  insightText: document.getElementById("insightText"),
};

// ---- Algorithm toggle buttons ----
els.algoButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    els.algoButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    selectedAlgo = btn.dataset.algo;
    updateCardVisibility();
  });
});

function updateCardVisibility() {
  els.lruCard.style.display = selectedAlgo === "optimal" ? "none" : "";
  els.optCard.style.display = selectedAlgo === "lru" ? "none" : "";
}
updateCardVisibility();

// ---- Table rendering ----
function renderTableHeader(headEl, frameCount) {
  headEl.innerHTML = "<th>Ref.</th>" +
    Array.from({ length: frameCount }, (_, i) => `<th>F${i + 1}</th>`).join("") +
    "<th>Status</th>";
}

function renderTableBody(bodyEl, result) {
  bodyEl.innerHTML = result.trace
    .map((step) => {
      const frameCells = step.frames
        .map((f) => `<td>${f === null ? "-" : f}</td>`)
        .join("");
      const statusClass = step.isFault ? "status-fault" : "status-hit";
      const statusText = step.isFault ? "Fault" : "Hit";
      return `<tr><td>${step.page}</td>${frameCells}<td class="${statusClass}">${statusText}</td></tr>`;
    })
    .join("");
}

// ---- Bar chart rendering (simple CSS-height bars, max height 110px) ----
function renderBar(barEl, valueEl, value, maxValue, label) {
  const MAX_HEIGHT = 110;
  const height = maxValue > 0 ? Math.max(6, (value / maxValue) * MAX_HEIGHT) : 6;
  barEl.style.height = `${height}px`;
  valueEl.textContent = label;
}

// ---- Insight text ----
function buildInsight(lruResult, optResult) {
  if (lruResult && optResult) {
    const gap = lruResult.totalFaults - optResult.totalFaults;
    if (gap > 0) {
      return `Optimal achieves ${gap} fewer page fault${gap === 1 ? "" : "s"} and a ` +
        `${(optResult.hitRatio - lruResult.hitRatio).toFixed(2)} higher hit ratio than LRU for this reference string.`;
    } else if (gap === 0) {
      return "LRU matched the Optimal benchmark exactly for this reference string.";
    }
  }
  if (lruResult && !optResult) {
    return `LRU produced ${lruResult.totalFaults} page faults (hit ratio ${lruResult.hitRatio}) for this reference string.`;
  }
  if (optResult && !lruResult) {
    return `Optimal produced ${optResult.totalFaults} page faults (hit ratio ${optResult.hitRatio}) — the theoretical minimum for this reference string.`;
  }
  return "Run a simulation to see how LRU compares with the Optimal benchmark for this reference string.";
}

// ---- Main run handler ----
function runSimulation() {
  els.errorBox.hidden = true;

  let referenceString, frameCount;
  try {
    ({ referenceString, frameCount } = validateInputs(els.refInput.value, els.frameInput.value));
  } catch (err) {
    if (err instanceof ValidationError) {
      els.errorBox.textContent = err.message;
      els.errorBox.hidden = false;
      return;
    }
    throw err;
  }

  const runLru = selectedAlgo !== "optimal";
  const runOpt = selectedAlgo !== "lru";

  let lruResult = null;
  let optResult = null;

  if (runLru) {
    lruResult = simulateLRU(referenceString, frameCount);
    renderTableHeader(els.lruTableHead, frameCount);
    renderTableBody(els.lruTableBody, lruResult);
    els.lruFaults.textContent = lruResult.totalFaults;
    els.lruHitRatio.textContent = lruResult.hitRatio;
  }

  if (runOpt) {
    optResult = simulateOptimal(referenceString, frameCount);
    renderTableHeader(els.optTableHead, frameCount);
    renderTableBody(els.optTableBody, optResult);
    els.optFaults.textContent = optResult.totalFaults;
    els.optHitRatio.textContent = optResult.hitRatio;
  }

  // Comparison panel only makes full sense when both ran; otherwise show
  // whichever ran and a dash for the other.
  els.cmpLruFaults.textContent = lruResult ? lruResult.totalFaults : "—";
  els.cmpOptFaults.textContent = optResult ? optResult.totalFaults : "—";
  els.cmpLruHit.textContent = lruResult ? lruResult.hitRatio : "—";
  els.cmpOptHit.textContent = optResult ? optResult.hitRatio : "—";

  const maxFault = Math.max(lruResult ? lruResult.totalFaults : 0, optResult ? optResult.totalFaults : 0, 1);
  renderBar(els.faultBarLru, els.faultBarLruVal, lruResult ? lruResult.totalFaults : 0, maxFault, lruResult ? lruResult.totalFaults : "-");
  renderBar(els.faultBarOpt, els.faultBarOptVal, optResult ? optResult.totalFaults : 0, maxFault, optResult ? optResult.totalFaults : "-");

  renderBar(els.hitBarLru, els.hitBarLruVal, lruResult ? lruResult.hitRatio : 0, 1, lruResult ? lruResult.hitRatio : "-");
  renderBar(els.hitBarOpt, els.hitBarOptVal, optResult ? optResult.hitRatio : 0, 1, optResult ? optResult.hitRatio : "-");

  els.insightText.textContent = buildInsight(lruResult, optResult);
}

els.runBtn.addEventListener("click", runSimulation);

// Run once on load with the pre-filled sample input (matches SLA1's reference string),
// so the simulator shows live results immediately rather than an empty screen.
window.addEventListener("DOMContentLoaded", () => {
  document.querySelector('.algo-btn[data-algo="lru"]').click();
  // Trigger both so the initial view mirrors the SLA1 mockup (both panels filled).
  selectedAlgo = "both";
  els.algoButtons.forEach((b) => b.classList.toggle("active", b.dataset.algo === "both"));
  updateCardVisibility();
  runSimulation();
});
