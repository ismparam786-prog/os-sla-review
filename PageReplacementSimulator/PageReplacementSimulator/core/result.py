"""
core.result
-----------
Common, algorithm-agnostic data structures used to report the outcome of a
page replacement simulation. Keeping these in one place means the LRU
module and the Optimal module return results in exactly the same shape,
which is what lets the CLI and the GUI display/compare them generically.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class StepRecord:
    """
    A single row of a page-replacement trace table: the state of the
    page frames immediately AFTER the given reference has been serviced.

    Attributes:
        step_index   : 1-based position of this reference in the string.
        page         : the page number that was referenced.
        frames       : snapshot of the frame contents, in frame order.
                       Empty/unused frames are represented by None.
        is_fault     : True if this reference caused a page fault.
        victim_page  : the page that was evicted to service this reference,
                       or None if no eviction took place (hit, or a free
                       frame was simply filled).
    """
    step_index: int
    page: int
    frames: List[int]
    is_fault: bool
    victim_page: int = None


@dataclass
class PageReplacementResult:
    """
    The full outcome of running one page replacement algorithm over one
    reference string with a fixed number of frames.

    Attributes:
        algorithm_name : human-readable name, e.g. "LRU" or "Optimal".
        frame_count    : number of page frames that were available.
        reference_string : the input sequence of page numbers.
        trace          : ordered list of StepRecord, one per reference.
        total_faults   : total number of page faults.
        total_hits     : total number of page hits.
        hit_ratio      : total_hits / len(reference_string), rounded to 2 dp.
        fault_ratio    : total_faults / len(reference_string), rounded to 2 dp.
    """
    algorithm_name: str
    frame_count: int
    reference_string: List[int]
    trace: List[StepRecord] = field(default_factory=list)

    @property
    def total_faults(self) -> int:
        return sum(1 for step in self.trace if step.is_fault)

    @property
    def total_hits(self) -> int:
        return sum(1 for step in self.trace if not step.is_fault)

    @property
    def hit_ratio(self) -> float:
        if not self.reference_string:
            return 0.0
        return round(self.total_hits / len(self.reference_string), 2)

    @property
    def fault_ratio(self) -> float:
        if not self.reference_string:
            return 0.0
        return round(self.total_faults / len(self.reference_string), 2)

    def as_dict(self) -> dict:
        """Serialize the result into a plain dict (used by the GUI's JSON bridge
        and by the CLI's optional --json output mode)."""
        return {
            "algorithm_name": self.algorithm_name,
            "frame_count": self.frame_count,
            "reference_string": self.reference_string,
            "total_faults": self.total_faults,
            "total_hits": self.total_hits,
            "hit_ratio": self.hit_ratio,
            "fault_ratio": self.fault_ratio,
            "trace": [
                {
                    "step_index": s.step_index,
                    "page": s.page,
                    "frames": s.frames,
                    "status": "Fault" if s.is_fault else "Hit",
                    "victim_page": s.victim_page,
                }
                for s in self.trace
            ],
        }
