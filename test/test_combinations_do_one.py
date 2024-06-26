import random
from typing import Any

random.seed(0)
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import DoOne


class TestDoOneMethodCombinations(unittest.TestCase):
    def setUp(test_self):
        test_self.elements = [random.randint(0, 1000) for _ in range(10)]

    def test_filter_sort_cmp(test_self):
        class T(DoOne):
            def filter(self, chosen) -> bool:
                return chosen % 2 == 0

            def sort_cmp(self, a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        expected_result = sorted([i for i in test_self.elements if i % 2 == 0])[0]
        result = inst(test_self.elements)
        test_self.assertTrue(
            result == expected_result,
        )

    def test_filter_sort_key(test_self):
        class T(DoOne):
            def filter(self, chosen) -> bool:
                return chosen % 2 == 0

            def sort_key(self, chosen):
                return chosen

        inst = T()
        result = inst(test_self.elements)
        test_self.assertTrue(
            result == sorted(list(filter(lambda x: x % 2 == 0, test_self.elements)))[0]
        )

    def test_filter_action(test_self):
        class T(DoOne):
            def filter(self, chosen: Any) -> bool:
                return chosen % 2 == 0

            def action(self, chosen: Any) -> Any:
                return chosen + 1

        inst = T()
        result = inst(test_self.elements)
        test_self.assertTrue(
            result == [i + 1 for i in test_self.elements if i % 2 == 0][0]
        )

    def test_sort_cmp_action(test_self):
        class T(DoOne):
            def sort_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any) -> Any:
                return chosen + 1

        inst = T()
        result = inst(test_self.elements)
        expected_result = sorted([i + 1 for i in test_self.elements])[0]
        test_self.assertTrue(result == expected_result)

    def test_sort_key_action(test_self):
        class T(DoOne):
            def sort_key(self, chosen: Any):
                return chosen

            def action(self, chosen):
                return chosen + 1

        inst = T()
        result = inst(test_self.elements)
        test_self.assertTrue(result == [i + 1 for i in sorted(test_self.elements)][0])

    def test_filter_sort_cmp_action(test_self):
        class T(DoOne):
            def filter(self, chosen: Any) -> bool:
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen):
                return chosen + 1

        inst = T()
        result = inst(test_self.elements)
        expected_results = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[0]
        test_self.assertTrue(result == expected_results)

    def test_filter_sort_key_action(test_self):
        class T(DoOne):
            def filter(self, chosen: Any) -> bool:
                return chosen % 2 == 0

            def sort_key(self, chosen: Any):
                return chosen

            def action(self, chosen: Any) -> Any:
                return chosen + 1

        inst = T()
        result = inst(test_self.elements)
        expected_result = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[0]
        test_self.assertTrue(result == expected_result)


if __name__ == "__main__":
    unittest.main()
