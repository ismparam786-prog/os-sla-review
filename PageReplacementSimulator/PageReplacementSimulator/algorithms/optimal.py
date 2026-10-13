"""
algorithms.optimal
--------------------
Optimal (Belady's / MIN) Page Replacement Algorithm.

Working principle
------------------
The Optimal algorithm evicts the page in memory that will NOT be used for
the longest time into the future (or is never used again). It requires
complete knowledge of the future reference string, which makes it
impossible to implement in a real, online operating system -- but it is
exactly this "look-ahead" property that makes it the theoretical benchmark:
no other algorithm can produce fewer page faults than Optimal for the same
reference string and frame count.

Implementation notes
---------------------
On every fault with no free frame available, we look ahead at the
remaining (not-yet-serviced) portion of the reference string once for each
resident page, to find its next use. The page with:

    * the FARTHEST next use is evicted, or
    * no next use at all (it is never referenced again) is evicted
      immediately, since that is unambiguously the best choice.

This is a direct, readable implementation rather than a heavily optimized
one (an optimized version would use pre-computed "next occurrence" indices
to avoid repeated linear scans) -- deliberately so, since the goal of this
simulator is to make the algorithm's logic easy to follow and verify by
hand against the trace table.
"""

from typing import List
from core.result import StepRecord, PageReplacementResult

ALGORITHM_NAME = "Optimal"


def _find_victim(memory: List[int], future_references: List[int]) -> int:
    """
    Given the pages currently resident in `memory` and the list of
    references still to come (`future_references`, i.e. everything AFTER
    the current step), return the page that should be evicted under the
    Optimal policy: the one used farthest in the future, or never again.
    """
    farthest_distance = -1
    victim = memory[0]

    for resident_page in memory:
        if resident_page in future_references:
            distance = future_references.index(resident_page)
        else:
            # Never used again -> evict this one immediately.
            return resident_page

        if distance > farthest_distance:
            farthest_distance = distance
            victim = resident_page

    return victim


def simulate_optimal(reference_string: List[int], frame_count: int) -> PageReplacementResult:
    """
    Run the Optimal page replacement algorithm over `reference_string`
    using `frame_count` page frames.

    Args:
        reference_string: ordered list of page numbers to access.
        frame_count: number of available page frames (>= 1).

    Returns:
        A PageReplacementResult containing the full step-by-step trace.
    """
    memory: List[int] = []
    trace: List[StepRecord] = []

    for index, page in enumerate(reference_string, start=1):
        victim_page = None

        if page in memory:
            is_fault = False
        else:
            is_fault = True
            if len(memory) < frame_count:
                memory.append(page)
            else:
                future_references = reference_string[index:]  # references after this one
                victim_page = _find_victim(memory, future_references)
                victim_index = memory.index(victim_page)
                memory[victim_index] = page

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
