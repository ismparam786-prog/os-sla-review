"""
algorithms package
-------------------
Contains the two traditional page replacement algorithms studied in this
project:

    * lru.py      -> Least Recently Used (LRU) Page Replacement
    * optimal.py  -> Optimal / Belady's (MIN) Page Replacement

Both modules expose a single public function, `simulate(reference_string,
frame_count)`, that returns a `PageReplacementResult` (see
`core.result.PageReplacementResult`) so that the CLI and GUI layers can treat
both algorithms identically.
"""

from .lru import simulate_lru
from .optimal import simulate_optimal

__all__ = ["simulate_lru", "simulate_optimal"]
