#!/usr/bin/env python3
"""
cli.py
------
Command-line interface for the Page Replacement Simulator.

This is the "console" implementation of the working model required for
SLA Review 2, point 7 (Implementation of the traditional algorithms).
It demonstrates:

    * accepting input from the user (interactive prompts, or --ref /
      --frames / --algo command-line flags for non-interactive use),
    * producing clearly understandable output (a formatted trace table
      plus a results summary),
    * handling valid and invalid input gracefully (via core.validator),
    * a few important edge cases: an empty reference string, a frame
      count of zero/negative, non-numeric input, and a frame count large
      enough that no page fault is ever a replacement (every page just
      fits in memory).

Usage (interactive):
    python cli.py

Usage (non-interactive):
    python cli.py --ref "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1" --frames 3 --algo both
"""

import argparse
import sys

from core.result import PageReplacementResult
from core.simulator import run_simulation, build_comparison_summary
from core.validator import ValidationError


def format_frame_cell(value) -> str:
    """Render an empty frame slot as '-' instead of 'None' for readability."""
    return "-" if value is None else str(value)


def print_trace_table(result: PageReplacementResult) -> None:
    """Print a neatly aligned trace table for one algorithm's result."""
    frame_headers = [f"F{i + 1}" for i in range(result.frame_count)]
    header = ["Step", "Ref"] + frame_headers + ["Status"]
    col_width = 7

    title = f" {result.algorithm_name} Trace (frames = {result.frame_count}) "
    print(title.center(col_width * len(header), "="))
    print("".join(h.center(col_width) for h in header))
    print("-" * (col_width * len(header)))

    for step in result.trace:
        row = [str(step.step_index), str(step.page)]
        row += [format_frame_cell(f) for f in step.frames]
        row.append("FAULT" if step.is_fault else "HIT")
        print("".join(cell.center(col_width) for cell in row))

    print("-" * (col_width * len(header)))
    print(f"Total Page Faults : {result.total_faults}")
    print(f"Total Page Hits   : {result.total_hits}")
    print(f"Hit Ratio         : {result.hit_ratio}")
    print(f"Fault Ratio       : {result.fault_ratio}")
    print()


def print_comparison(results) -> None:
    """Print a short side-by-side comparison when both algorithms were run."""
    if len(results) < 2:
        return
    summary = build_comparison_summary(results)
    print("=" * 40)
    print(" Performance Comparison")
    print("=" * 40)
    print(f"{'Algorithm':<12}{'Faults':<10}{'Hit Ratio':<10}")
    for key, data in summary.items():
        if key == "efficiency_gap":
            continue
        name = results[key].algorithm_name
        print(f"{name:<12}{data['total_faults']:<10}{data['hit_ratio']:<10}")
    gap = summary.get("efficiency_gap")
    if gap is not None:
        if gap > 0:
            print(f"\nOptimal produces {gap} fewer page fault(s) than LRU "
                  f"for this reference string.")
        elif gap == 0:
            print("\nLRU matched Optimal exactly for this reference string.")
    print()


def run_interactive() -> None:
    """Prompt the user for input, re-prompting on invalid entries."""
    print("=" * 50)
    print(" Page Replacement Simulator (LRU & Optimal) ")
    print("=" * 50)

    while True:
        raw_ref = input(
            "\nEnter the reference string (e.g. 7,0,1,2,0,3,0,4): "
        )
        raw_frames = input("Enter the number of page frames: ")
        algo_choice = input(
            "Choose algorithm - [L]RU, [O]ptimal, or [B]oth (default B): "
        ).strip().lower()

        algo_map = {"l": "lru", "o": "optimal", "b": "both", "": "both"}
        algorithm = algo_map.get(algo_choice)
        if algorithm is None:
            print("Invalid choice. Please enter L, O, or B.")
            continue

        try:
            results = run_simulation(raw_ref, raw_frames, algorithm)
        except ValidationError as err:
            # Handle invalid input: show the message and let the user retry
            # rather than crashing.
            print(f"\n[Input Error] {err}\nPlease try again.\n")
            continue

        for result in results.values():
            print_trace_table(result)
        print_comparison(results)
        break


def run_non_interactive(args: argparse.Namespace) -> int:
    """Run once from --ref/--frames/--algo flags; returns a process exit code."""
    try:
        results = run_simulation(args.ref, args.frames, args.algo)
    except ValidationError as err:
        print(f"[Input Error] {err}", file=sys.stderr)
        return 1
    except ValueError as err:
        print(f"[Error] {err}", file=sys.stderr)
        return 1

    for result in results.values():
        print_trace_table(result)
    print_comparison(results)
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate LRU and Optimal page replacement on a reference string."
    )
    parser.add_argument(
        "--ref", type=str, default=None,
        help="Comma/space-separated reference string, e.g. '7,0,1,2,0,3,0,4'",
    )
    parser.add_argument(
        "--frames", type=str, default=None,
        help="Number of page frames (positive integer).",
    )
    parser.add_argument(
        "--algo", type=str, default="both", choices=["lru", "optimal", "both"],
        help="Which algorithm to run (default: both).",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.ref is not None and args.frames is not None:
        sys.exit(run_non_interactive(args))
    else:
        run_interactive()


if __name__ == "__main__":
    main()
