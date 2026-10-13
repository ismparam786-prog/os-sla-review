# Page Replacement Simulator — LRU & Optimal

Self-Learning Activity (Operating Systems) — SLA Review 2
Topic: **Page Replacement Techniques – LRU and Optimal Algorithm for Virtual Memory Management**

Team:
- Param Patel — SYCM2-36 (125BTCM1078)
- Jainam Shah — SYCM2-47 (125BTCM1034)

Class/Batch: SYCM2-B · Faculty: Ms. Deepshikha Chaturvedi

---

## What this project contains

| Part | Location | Purpose |
|---|---|---|
| Algorithm core | `algorithms/lru.py`, `algorithms/optimal.py` | The two traditional page replacement algorithms, as pure, well-documented functions. |
| Shared data model | `core/result.py` | `StepRecord` / `PageReplacementResult` — the common shape both algorithms return. |
| Input validation | `core/validator.py` | Parses and validates the reference string & frame count; raises `ValidationError` with a clear message on bad input. |
| Orchestration | `core/simulator.py` | Ties validation + algorithm selection together; used by both the CLI and the GUI's logic. |
| Console program | `cli.py` | Interactive or `--ref/--frames/--algo` command-line driver with full I/O handling. |
| Automated tests | `tests/test_algorithms.py` | 16 unit tests, incl. a regression check against the exact SLA Review 1 figures (LRU = 12 faults, Optimal = 9 faults). |
| GUI | `gui/index.html` + `gui/css/style.css` + `gui/js/*.js` | Working browser-based prototype that visually matches the SLA Review 1 wireframe mockup. |

## Running the console program

```bash
# Interactive mode (prompts for input, re-prompts on invalid entries)
python cli.py

# Non-interactive mode
python cli.py --ref "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1" --frames 3 --algo both
```

`--algo` accepts `lru`, `optimal`, or `both` (default).

## Running the automated tests

```bash
python -m unittest discover -s tests -v
```

## Running the GUI

The GUI is a self-contained static web page — no server or build step required:

```bash
# simply open gui/index.html in any modern browser, e.g.
open gui/index.html        # macOS
xdg-open gui/index.html    # Linux
start gui\index.html       # Windows
```

It loads with the sample SLA1 reference string pre-filled and both algorithms
run automatically, so the comparison panels are populated immediately.

### GUI features (per the assignment's GUI checklist)

1. **Enter required input** — reference string (comma/space separated) and number of frames.
2. **Select Algorithm 1 or 2** — LRU / Optimal / Both toggle buttons.
3. **Execute the simulation** — "Run Simulation" button.
4. **View the algorithm execution / results** — full step-by-step frame trace table with Hit/Fault status per reference.
5. **Compare the performance of both algorithms** — side-by-side Performance Comparison panel, Page Fault Comparison bar chart, Hit Ratio Comparison bar chart, and an auto-generated Key Insight sentence.

Invalid input (empty string, non-integer page, negative page, zero/non-numeric frame count) is caught by `gui/js/validator.js` — the same rules as `core/validator.py` — and shown as an inline error message instead of breaking the simulation.

## Design notes

* The LRU implementation tracks recency with a list, `recent_use`, that is
  kept in exact sync with the contents of memory on every step. This
  invariant — explained in the docstring of `algorithms/lru.py` — is what
  prevents a subtle class of bug where an evicted page's stale recency entry
  corrupts a later eviction decision.
* The Optimal implementation looks ahead into the remaining reference string
  on each fault to find the resident page used farthest in the future (or
  never again), exactly as described in the SLA Review 1 report.
* `gui/js/algorithms.js` is a direct, line-for-line JavaScript mirror of the
  Python algorithms, so the GUI and the console program can never disagree
  on fault counts for the same input.
