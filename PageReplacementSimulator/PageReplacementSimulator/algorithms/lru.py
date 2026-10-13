"""
algorithms.lru
---------------
Least Recently Used (LRU) Page Replacement Algorithm.

Working principle
------------------
LRU assumes locality of reference: a page that was used recently is likely
to be used again soon, and a page that has not been used for a long time is
unlikely to be needed again soon. When a page fault occurs and memory is
full, LRU evicts the page that has gone the LONGEST without being
referenced.

Implementation notes
---------------------
We track recency with a simple list, `recent_use`, that always contains
EXACTLY the pages currently resident in memory, ordered oldest-to-newest.
This invariant is the key correctness property of this implementation:

    * On a HIT, the referenced page is moved to the end of `recent_use`
      (marking it as most-recently-used).
    * On a FAULT with a free frame available, the new page is appended to
      memory and to the end of `recent_use`.
    * On a FAULT with no free frame, the page at the FRONT of `recent_use`
      (the least-recently-used resident page) is popped as the victim,
      evicted from memory, and the new page takes its place and is pushed
      onto the end of `recent_use`.

Keeping `recent_use` free of stale (already-evicted) entries is essential;
an earlier draft of this simulator kept evicted pages in the recency list,
which silently corrupted later eviction decisions. Maintaining the
"recent_use mirrors memory contents" invariant on every single step avoids
that class of bug entirely.
"""

from typing import List
from core.result import StepRecord, PageReplacementResult

ALGORITHM_NAME = "LRU"


def simulate_lru(reference_string: List[int], frame_count: int) -> PageReplacementResult:
    """
    Run the LRU page replacement algorithm over `reference_string` using
    `frame_count` page frames.

    Args:
        reference_string: ordered list of page numbers to access.
        frame_count: number of available page frames (>= 1).

    Returns:
        A PageReplacementResult containing the full step-by-step trace.
    """
    memory: List[int] = []           # pages currently resident, in frame order
    recent_use: List[int] = []       # oldest-first list of resident pages
    trace: List[StepRecord] = []

    for index, page in enumerate(reference_string, start=1):
        victim_page = None

        if page in memory:
            # --- HIT: bump this page to most-recently-used ---
            is_fault = False
            recent_use.remove(page)
            recent_use.append(page)
        else:
            # --- FAULT: the page must be brought into memory ---
            is_fault = True
            if len(memory) < frame_count:
                # A free frame is still available -> no eviction needed.
                memory.append(page)
            else:
                # Memory is full -> evict the least-recently-used page.
                victim_page = recent_use.pop(0)
                victim_index = memory.index(victim_page)
                memory[victim_index] = page
            recent_use.append(page)

        # Snapshot the frame contents (padded with None for empty frames)
        # so the GUI/CLI can render a fixed-width table regardless of how
        # many frames are currently filled.
        frame_snapshot = memory + [None] * (frame_count - len(memory))

        trace.append(
            StepRecord(
                step_index=index,
                page=page,
                frames=frame_snapshot,
                is_fault=is_fault,
                victim_page=victim_page,
            )
        )

    return PageReplacementResult(
        algorithm_name=ALGORITHM_NAME,
        frame_count=frame_count,
        reference_string=reference_string,
        trace=trace,
    )
