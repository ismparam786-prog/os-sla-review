# OS SLA Review 2 — Page Replacement Simulator

A modular implementation of **Least Recently Used (LRU)** and **Optimal (Belady's MIN)** page-replacement algorithms for virtual memory management. This project accompanies the Operating Systems SLA Review 2 submission by Param Patel (SYCM2-36) and Jainam Shah (SYCM2-47).

## Features

- LRU and Optimal page-replacement simulations.
- Console interface (CLI) with interactive and command-line modes.
- Browser GUI with step-by-step frame traces, hit/fault status, metric cards, and comparisons.
- Shared validation rules for page references and frame counts.
- Metrics: page faults, page hits, hit ratio, fault ratio, and comparative fault gap.
- 16 automated unit tests.

## Project structure

```text
PageReplacementSimulator/
├── algorithms/
│   ├── __init__.py
│   ├── lru.py
│   └── optimal.py
├── core/
│   ├── __init__.py
│   ├── result.py
│   ├── validator.py
│   └── simulator.py
├── tests/
│   └── test_algorithms.py
├── gui/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── algorithms.js
│       ├── validator.js
│       └── app.js
├── cli.py
└── README.md
```

## Requirements

- Python 3.10 or newer for the CLI and tests.
- A modern browser for the GUI. No JavaScript packages or build step are required.

## Run the CLI

From the repository root:

```bash
python cli.py
```

Run a specific reference string with three frames using both algorithms:

```bash
python cli.py --ref "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1" --frames 3 --algo both
```

Supported algorithm values: `lru`, `optimal`, and `both`. Reference values may be comma- or space-separated.

## Open the browser GUI

Open `gui/index.html` directly in a browser, or serve the repository locally:

```bash
python -m http.server 8000
```

Then visit [http://localhost:8000/gui/](http://localhost:8000/gui/).

## Run tests

```bash
python -m unittest discover -s tests -v
```

The SLA Review 1 reference string above should produce **12 page faults for LRU** and **9 for Optimal** with three frames (hit ratios 0.40 and 0.55 respectively).

## Input validation

- Empty reference strings are rejected.
- Page numbers must be non-negative integers.
- Frame count must be an integer from 1 to 50.
- Comma-separated and space-separated page references are both supported.
- If the number of frames can hold all distinct pages, no replacement is needed.

## Authors

- Param Patel — SYCM2-36
- Jainam Shah — SYCM2-47

Operating Systems · SLA Review 2 · Semester III
