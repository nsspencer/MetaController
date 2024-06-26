import random
from typing import Any

random.seed(0)
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import DoOne


class ArgCheck:
    def __init__(
        self,
        filter_passed=False,
        sort_cmp_passed=False,
        sort_key_passed=False,
        action_passed=False,
        fold_passed=False,
    ) -> None:
        self.filter_passed = filter_passed
        self.sort_cmp_passed = sort_cmp_passed
        self.sort_key_passed = sort_key_passed
        self.action_passed = action_passed
        self.fold_passed = fold_passed


class TestDoOneMethodCombinationsWithArg(unittest.TestCase):
    def setUp(test_self):
        test_self.elements = [random.randint(0, 1000) for _ in range(10)]

    def test_filter_sort_cmp(test_self):
        class T(DoOne):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a, b, arg):
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

        arg = ArgCheck()
        inst = T()
        expected_result = sorted([i for i in test_self.elements if i % 2 == 0])[0]
        result = inst(test_self.elements, arg)
        test_self.assertTrue(
            result == expected_result,
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)

    def test_filter_sort_key(test_self):
        class T(DoOne):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen, arg):
                arg.sort_key_passed = True
                return chosen

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.elements, arg)
        test_self.assertTrue(
            result == sorted(list(filter(lambda x: x % 2 == 0, test_self.elements)))[0]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)

    def test_filter_action(test_self):
        class T(DoOne):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.elements, arg)
        test_self.assertTrue(
            result == [i + 1 for i in test_self.elements if i % 2 == 0][0]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_cmp_action(test_self):
        class T(DoOne):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements])[0]
        test_self.assertTrue(result == expected_result)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_key_action(test_self):
        class T(DoOne):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.elements, arg)
        test_self.assertTrue(result == [i + 1 for i in sorted(test_self.elements)][0])
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_cmp_action(test_self):
        class T(DoOne):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.elements, arg)
        expected_results = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[0]
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_key_action(test_self):
        class T(DoOne):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[0]
        test_self.assertTrue(result == expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)


if __name__ == "__main__":
    unittest.main()
