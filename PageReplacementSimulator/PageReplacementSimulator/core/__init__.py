"""core package: shared data structures and input validation."""

from .result import StepRecord, PageReplacementResult
from .validator import validate_inputs, ValidationError

__all__ = [
    "StepRecord",
    "PageReplacementResult",
    "validate_inputs",
    "ValidationError",
]
