"""
core.simulator
----------------
Thin orchestration layer that ties input validation + the two algorithm
modules together, and produces a side-by-side comparison summary. This is
the single entry point both `cli.py` and the GUI backend bridge call into,
so validation and algorithm selection logic is written exactly once.
"""

from typing import Dict
from algorithms import simulate_lru, simulate_optimal
from core.result import PageReplacementResult
from core.validator import validate_inputs

SUPPORTED_ALGORITHMS = {
    "lru": simulate_lru,
    "optimal": simulate_optimal,
}


def run_simulation(raw_reference_string: str, raw_frame_count, algorithm: str = "both") -> Dict[str, PageReplacementResult]:
    """
    Validate input, then run the requested algorithm(s).

    Args:
        raw_reference_string: unparsed reference string from the user.
        raw_frame_count: unparsed frame count from the user.
        algorithm: one of "lru", "optimal", or "both" (default).

    Returns:
        dict mapping algorithm key -> PageReplacementResult, e.g.
        {"lru": <result>, "optimal": <result>} when algorithm="both".

    Raises:
        core.validator.ValidationError: if the inputs are invalid.
        ValueError: if `algorithm` is not a recognised option.
    """
    reference_string, frame_count = validate_inputs(raw_reference_string, raw_frame_count)

    algorithm = algorithm.lower().strip()
    if algorithm == "both":
        selected = list(SUPPORTED_ALGORITHMS.items())
    elif algorithm in SUPPORTED_ALGORITHMS:
        selected = [(algorithm, SUPPORTED_ALGORITHMS[algorithm])]
    else:
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. Choose from: "
            f"{', '.join(list(SUPPORTED_ALGORITHMS) + ['both'])}."
        )

    return {key: fn(reference_string, frame_count) for key, fn in selected}


def build_comparison_summary(results: Dict[str, PageReplacementResult]) -> Dict:
    """
    Build a small, display-ready comparison summary (used by both the CLI's
    tabular summary and the GUI's "Performance Comparison" panel).

    Returns a dict shaped like:
        {
            "lru":     {"total_faults": 12, "hit_ratio": 0.40},
            "optimal": {"total_faults": 9,  "hit_ratio": 0.55},
            "efficiency_gap": 3   # only present if both algorithms were run
        }
    """
    summary = {
        key: {"total_faults": r.total_faults, "hit_ratio": r.hit_ratio}
        for key, r in results.items()
    }
    if "lru" in results and "optimal" in results:
        summary["efficiency_gap"] = results["lru"].total_faults - results["optimal"].total_faults
    return summary
