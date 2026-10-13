/**
 * algorithms.js
 * --------------
 * Browser-side mirror of the Python LRU / Optimal implementations in
 * algorithms/lru.py and algorithms/optimal.py. The logic here is kept
 * IDENTICAL, step for step, to the Python version so that the GUI and the
 * console program always agree on fault counts and trace tables for the
 * same input (this is checked by hand against tests/test_algorithms.py).
 *
 * Both functions return a plain object:
 *   {
 *     algorithmName: "LRU" | "Optimal",
 *     frameCount: number,
 *     referenceString: number[],
 *     trace: [{ stepIndex, page, frames: (number|null)[], isFault, victimPage }],
 *     totalFaults, totalHits, hitRatio, faultRatio
 *   }
 */

function finalizeResult(algorithmName, frameCount, referenceString, trace) {
  const totalFaults = trace.filter((s) => s.isFault).length;
  const totalHits = trace.length - totalFaults;
  const hitRatio = referenceString.length
    ? Math.round((totalHits / referenceString.length) * 100) / 100
    : 0;
  const faultRatio = referenceString.length
    ? Math.round((totalFaults / referenceString.length) * 100) / 100
    : 0;

  return {
    algorithmName,
    frameCount,
    referenceString,
    trace,
    totalFaults,
    totalHits,
    hitRatio,
    faultRatio,
  };
}

/** Least Recently Used (LRU) page replacement. See algorithms/lru.py for the full explanation. */
function simulateLRU(referenceString, frameCount) {
  const memory = [];     // pages currently resident, in frame order
  let recentUse = [];    // oldest-first list of resident pages (mirrors `memory`)
  const trace = [];

  referenceString.forEach((page, i) => {
    const stepIndex = i + 1;
    let isFault = false;
    let victimPage = null;

    if (memory.includes(page)) {
      // HIT: bump this page to most-recently-used.
      recentUse = recentUse.filter((p) => p !== page);
      recentUse.push(page);
    } else {
      isFault = true;
      if (memory.length < frameCount) {
        memory.push(page);
      } else {
        victimPage = recentUse.shift(); // least-recently-used resident page
        const victimIndex = memory.indexOf(victimPage);
        memory[victimIndex] = page;
      }
      recentUse.push(page);
    }

    const frames = memory.concat(Array(frameCount - memory.length).fill(null));
    trace.push({ stepIndex, page, frames: frames.slice(), isFault, victimPage });
  });

  return finalizeResult("LRU", frameCount, referenceString, trace);
}

/** Find the Optimal victim: the resident page used farthest in the future, or never again. */
function findOptimalVictim(memory, futureReferences) {
  let farthestDistance = -1;
  let victim = memory[0];

  for (const residentPage of memory) {
    const distance = futureReferences.indexOf(residentPage);
    if (distance === -1) {
      return residentPage; // never used again -> evict immediately
    }
    if (distance > farthestDistance) {
      farthestDistance = distance;
      victim = residentPage;
    }
  }
  return victim;
}

/** Optimal (Belady's / MIN) page replacement. See algorithms/optimal.py for the full explanation. */
function simulateOptimal(referenceString, frameCount) {
  const memory = [];
  const trace = [];

  referenceString.forEach((page, i) => {
    const stepIndex = i + 1;
    let isFault = false;
    let victimPage = null;

    if (memory.includes(page)) {
      isFault = false;
    } else {
      isFault = true;
      if (memory.length < frameCount) {
        memory.push(page);
      } else {
        const futureReferences = referenceString.slice(i + 1);
        victimPage = findOptimalVictim(memory, futureReferences);
        const victimIndex = memory.indexOf(victimPage);
        memory[victimIndex] = page;
      }
    }

    const frames = memory.concat(Array(frameCount - memory.length).fill(null));
    trace.push({ stepIndex, page, frames: frames.slice(), isFault, victimPage });
  });

  return finalizeResult("Optimal", frameCount, referenceString, trace);
}
