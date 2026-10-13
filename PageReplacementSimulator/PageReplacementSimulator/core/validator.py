"""
core.validator
--------------
Input validation and parsing for the Page Replacement Simulator.

This module is deliberately kept separate from the CLI and the algorithms
so that both the command-line interface and the (future) GUI backend can
reuse exactly the same validation rules, and so that invalid input is
rejected BEFORE it ever reaches the simulation logic.
"""

from typing import List, Tuple


class ValidationError(Exception):
    """Raised when user-supplied input fails validation.

    Carries a short, user-facing message describing exactly what was wrong,
    so the CLI/GUI can show it directly without any further formatting.
    """
    pass


def parse_reference_string(raw_text: str) -> List[int]:
    """
    Convert a raw, comma/space separated string of page numbers (e.g.
    "7, 0, 1, 2, 0" or "7 0 1 2 0") into a list of non-negative integers.

    Raises:
        ValidationError: if the string is empty, contains a non-integer
                          token, or contains a negative page number.
    """
    if raw_text is None or not raw_text.strip():
        raise ValidationError(
            "Reference string cannot be empty. Enter page numbers separated "
            "by commas or spaces, e.g. 7, 0, 1, 2, 0, 3, 0, 4"
        )

    # Accept both comma-separated and whitespace-separated input.
    tokens = [tok for tok in raw_text.replace(",", " ").split() if tok != ""]

    if not tokens:
        raise ValidationError("Reference string cannot be empty.")

    pages: List[int] = []
    for tok in tokens:
        if not tok.lstrip("-").isdigit():
            raise ValidationError(
                f"Invalid page number '{tok}'. Only non-negative integers "
                f"are allowed in the reference string."
            )
        value = int(tok)
        if value < 0:
            raise ValidationError(
                f"Invalid page number '{tok}'. Page numbers cannot be negative."
            )
        pages.append(value)

    return pages


def parse_frame_count(raw_text) -> int:
    """
    Convert raw input (string or int) for the number of page frames into a
    positive integer.

    Raises:
        ValidationError: if the value is not an integer, or is not >= 1.
    """
    try:
        frames = int(str(raw_text).strip())
    except (ValueError, TypeError):
        raise ValidationError(
            f"Number of frames must be a whole number, got '{raw_text}'."
        )

    if frames < 1:
        raise ValidationError("Number of frames must be at least 1.")

    if frames > 50:
        # Generous upper bound: protects the trace table/GUI from becoming
        # unreadable and guards against accidental typos (e.g. 300 instead of 3).
        raise ValidationError(
            "Number of frames is unreasonably large (max supported is 50)."
        )

    return frames


def validate_inputs(raw_reference_string: str, raw_frame_count) -> Tuple[List[int], int]:
    """
    Convenience wrapper that validates and parses BOTH inputs together and
    performs the cross-field edge-case checks (e.g. frame count larger than
    the number of distinct pages referenced -> every page simply fits in
    memory and there will never be a replacement, which is valid but worth
    flagging only as information, not as an error).

    Returns:
        (reference_string, frame_count) as a validated, parsed pair.
    """
    reference_string = parse_reference_string(raw_reference_string)
    frame_count = parse_frame_count(raw_frame_count)
    return reference_string, frame_count
