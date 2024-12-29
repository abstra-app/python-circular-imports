from unittest import TestCase
from .graph import find_cycles, normalize_cycle


class TestNormalizeCycle(TestCase):
    def test_normalize_cycle_abc(self):
        cycle_a = ["a", "b", "c"]
        cycle_b = ["b", "c", "a"]
        cycle_c = ["c", "a", "b"]

        self.assertEqual(normalize_cycle(cycle_a), ["a", "b", "c"])
        self.assertEqual(normalize_cycle(cycle_b), ["a", "b", "c"])
        self.assertEqual(normalize_cycle(cycle_c), ["a", "b", "c"])


class TestFindCycles(TestCase):
    def test_find_cycles(self):
        graph = {("a", "b"), ("b", "a")}
        cycles = find_cycles(graph)
        self.assertEqual(cycles, [["a", "b"]])

    def test_find_long_cycles(self):
        graph = {("a", "b"), ("b", "c"), ("c", "a")}
        cycles = find_cycles(graph)
        self.assertEqual(cycles, [["a", "b", "c"]])
