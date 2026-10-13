"""
tests.test_algorithms
-----------------------
Basic correctness tests for the LRU and Optimal implementations.

Run with:
    python -m unittest discover -s tests -v
from the project root (PageReplacementSimulator/).

The main regression test below uses the exact reference string and frame
count from SLA Review 1 of this project, and asserts the fault counts
match the hand-verified values reported there (LRU = 12 faults,
Optimal = 9 faults), so any future change to the algorithms that breaks
correctness is caught immediately.
"""

import os
import sys
import unittest

# Make the project root importable when running this file directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import simulate_lru, simulate_optimal
from core.validator import validate_inputs, ValidationError


# The exact reference string used throughout SLA Review 1 of this project.
SLA1_REFERENCE_STRING = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
SLA1_FRAME_COUNT = 3


class TestLRU(unittest.TestCase):
    def test_sla1_reference_string_matches_report(self):
        result = simulate_lru(SLA1_REFERENCE_STRING, SLA1_FRAME_COUNT)
        self.assertEqual(result.total_faults, 12)
        self.assertEqual(result.total_hits, 8)
        self.assertEqual(result.hit_ratio, 0.40)

    def test_first_n_distinct_pages_are_always_faults(self):
        # The first `frame_count` distinct pages can never be hits, since
        # memory starts empty.
        result = simulate_lru([5, 6, 7], frame_count=3)
        self.assertEqual(result.total_faults, 3)
        self.assertEqual(result.total_hits, 0)

    def test_repeating_single_page_is_always_a_hit_after_the_first(self):
        result = simulate_lru([1, 1, 1, 1], frame_count=1)
        self.assertEqual(result.total_faults, 1)
        self.assertEqual(result.total_hits, 3)

    def test_single_frame_always_evicts_current_page(self):
        # With exactly 1 frame, every distinct new reference is a fault.
        result = simulate_lru([1, 2, 1, 2], frame_count=1)
        self.assertEqual(result.total_faults, 4)

    def test_frame_snapshot_width_matches_frame_count(self):
        result = simulate_lru([1, 2], frame_count=4)
        for step in result.trace:
            self.assertEqual(len(step.frames), 4)


class TestOptimal(unittest.TestCase):
    def test_sla1_reference_string_matches_report(self):
        result = simulate_optimal(SLA1_REFERENCE_STRING, SLA1_FRAME_COUNT)
        self.assertEqual(result.total_faults, 9)
        self.assertEqual(result.total_hits, 11)
        self.assertEqual(result.hit_ratio, 0.55)

    def test_optimal_never_worse_than_lru(self):
        # Optimal is, by definition, the theoretical minimum: it can never
        # produce MORE faults than LRU for the same input.
        lru_result = simulate_lru(SLA1_REFERENCE_STRING, SLA1_FRAME_COUNT)
        opt_result = simulate_optimal(SLA1_REFERENCE_STRING, SLA1_FRAME_COUNT)
        self.assertLessEqual(opt_result.total_faults, lru_result.total_faults)

    def test_page_never_referenced_again_is_evicted_first(self):
        # frames=2; page 9 is never seen again after index 0, so it should
        # be evicted before page 8 (used again at index 3) when a 3rd
        # distinct page forces an eviction.
        result = simulate_optimal([9, 8, 7, 8], frame_count=2)
        fault_step = result.trace[2]  # the reference to page 7
        self.assertTrue(fault_step.is_fault)
        self.assertEqual(fault_step.victim_page, 9)


class TestValidator(unittest.TestCase):
    def test_valid_input_parses_correctly(self):
        pages, frames = validate_inputs("7, 0, 1, 2", "3")
        self.assertEqual(pages, [7, 0, 1, 2])
        self.assertEqual(frames, 3)

    def test_space_separated_input_also_works(self):
        pages, _ = validate_inputs("7 0 1 2", "3")
        self.assertEqual(pages, [7, 0, 1, 2])

    def test_empty_reference_string_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_inputs("", "3")

    def test_non_integer_page_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_inputs("7, a, 1", "3")

    def test_negative_page_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_inputs("7, -1, 1", "3")

    def test_zero_frames_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_inputs("7, 0, 1", "0")

    def test_non_integer_frame_count_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_inputs("7, 0, 1", "abc")

    def test_excessively_large_frame_count_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_inputs("7, 0, 1", "1000")


if __name__ == "__main__":
    unittest.main()
