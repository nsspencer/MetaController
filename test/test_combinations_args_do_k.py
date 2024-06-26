import random
from typing import Any, List

random.seed(0)
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import DoK


class ArgCheck:
    def __init__(self):
        self.filter_passed = False
        self.sort_cmp_passed = False
        self.sort_key_passed = False
        self.action_passed = False
        self.fold_passed = False


class TestDoK0MethodCombinationsWithArg(unittest.TestCase):
    def setUp(test_self):
        test_self.elements = [random.randint(0, 1000) for _ in range(10)]
        test_self.k = 0

    def test_filter_sort_cmp(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a, b, arg):
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

        arg = ArgCheck()
        inst = T()
        expected_result = sorted([i for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(result, expected_result)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_cmp_passed)

    def test_filter_sort_key(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen, arg):
                arg.sort_key_passed = True
                return chosen

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sorted(list(filter(lambda x: x % 2 == 0, test_self.elements)))[
                : test_self.k
            ]
        )
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_key_passed)

    def test_filter_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.action_passed)

    def test_filter_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sum(
                list(filter(lambda x: x % 2 == 0, test_self.elements))[: test_self.k]
            )
        )
        test_self.assertFalse(arg.filter_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements])[: test_self.k]
        test_self.assertListEqual(result, expected_result)
        test_self.assertFalse(arg.sort_cmp_passed)
        test_self.assertFalse(arg.action_passed)

    def test_sort_cmp_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertFalse(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(
            result, sorted([i + 1 for i in sorted(test_self.elements)][: test_self.k])
        )
        test_self.assertFalse(arg.sort_key_passed)
        test_self.assertFalse(arg.action_passed)

    def test_sort_key_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertFalse(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_action_fold(test_self):
        class T(DoK):
            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, [i + 1 for i in test_self.elements[: test_self.k]]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == sum([i + 1 for i in test_self.elements][: test_self.k])
        )
        test_self.assertFalse(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sorted(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertListEqual(result, expected_results)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_cmp_passed)
        test_self.assertFalse(arg.action_passed)

    def test_filter_sort_cmp_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        test_self.assertListEqual(result, expected_result)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_key_passed)
        test_self.assertFalse(arg.action_passed)

    def test_filter_sort_key_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.sort_cmp_passed)
        test_self.assertFalse(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.sort_key_passed)
        test_self.assertFalse(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_cmp_passed)
        test_self.assertFalse(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertFalse(arg.filter_passed)
        test_self.assertFalse(arg.sort_key_passed)
        test_self.assertFalse(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)


class TestDoK1MethodCombinationsWithArg(unittest.TestCase):
    def setUp(test_self):
        test_self.elements = [random.randint(0, 1000) for _ in range(10)]
        test_self.k = 1

    def test_filter_sort_cmp(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a, b, arg):
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

        arg = ArgCheck()
        inst = T()
        expected_result = sorted([i for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)

    def test_filter_sort_key(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen, arg):
                arg.sort_key_passed = True
                return chosen

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sorted(list(filter(lambda x: x % 2 == 0, test_self.elements)))[
                : test_self.k
            ]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)

    def test_filter_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sum(
                list(filter(lambda x: x % 2 == 0, test_self.elements))[: test_self.k]
            )
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements])[: test_self.k]
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_cmp_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(
            result, sorted([i + 1 for i in sorted(test_self.elements)][: test_self.k])
        )
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_key_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_action_fold(test_self):
        class T(DoK):
            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, [i + 1 for i in test_self.elements[: test_self.k]]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == sum([i + 1 for i in test_self.elements][: test_self.k])
        )
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        test_self.assertListEqual(result, expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_cmp_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_key_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)


class TestDoK5MethodCombinationsWithArg(unittest.TestCase):
    def setUp(test_self):
        test_self.elements = [random.randint(0, 1000) for _ in range(10)]
        test_self.k = 5

    def test_filter_sort_cmp(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a, b, arg):
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

        arg = ArgCheck()
        inst = T()
        expected_result = sorted([i for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)

    def test_filter_sort_key(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen, arg):
                arg.sort_key_passed = True
                return chosen

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sorted(list(filter(lambda x: x % 2 == 0, test_self.elements)))[
                : test_self.k
            ]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)

    def test_filter_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sum(
                list(filter(lambda x: x % 2 == 0, test_self.elements))[: test_self.k]
            )
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements])[: test_self.k]
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_cmp_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(
            result, sorted([i + 1 for i in sorted(test_self.elements)][: test_self.k])
        )
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_key_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_action_fold(test_self):
        class T(DoK):
            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, [i + 1 for i in test_self.elements[: test_self.k]]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == sum([i + 1 for i in test_self.elements][: test_self.k])
        )
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sorted(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertListEqual(result, expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_cmp_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_key_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)


class TestDoKAllMethodCombinationsWithArg(unittest.TestCase):
    def setUp(test_self):
        test_self.elements = [random.randint(0, 1000) for _ in range(10)]
        test_self.k = 10

    def test_filter_sort_cmp(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a, b, arg):
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

        arg = ArgCheck()
        inst = T()
        expected_result = sorted([i for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)

    def test_filter_sort_key(test_self):
        class T(DoK):
            def filter(self, chosen, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen, arg):
                arg.sort_key_passed = True
                return chosen

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sorted(list(filter(lambda x: x % 2 == 0, test_self.elements)))[
                : test_self.k
            ]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)

    def test_filter_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result
            == sum(
                list(filter(lambda x: x % 2 == 0, test_self.elements))[: test_self.k]
            )
        )
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements])[: test_self.k]
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_cmp_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertListEqual(
            result, sorted([i + 1 for i in sorted(test_self.elements)][: test_self.k])
        )
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_sort_key_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, sorted(test_self.elements)[: test_self.k]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(result == sum(sorted(test_self.elements)[: test_self.k]))
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_action_fold(test_self):
        class T(DoK):
            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results, [i + 1 for i in test_self.elements[: test_self.k]]
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        test_self.assertTrue(
            result == sum([i + 1 for i in test_self.elements][: test_self.k])
        )
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sorted(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertListEqual(result, expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_cmp_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
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
        result = inst(test_self.k, test_self.elements, arg)
        expected_result = sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
            : test_self.k
        ]
        test_self.assertListEqual(result, expected_result)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)

    def test_filter_sort_key_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            [i + 1 for i in test_self.elements if i % 2 == 0][: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_cmp_action_fold(test_self):
        class T(DoK):
            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen, arg):
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_sort_key_action_fold(test_self):
        class T(DoK):
            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements])[: test_self.k],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_cmp_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_cmp(self, a: Any, b: Any, arg) -> int:
                arg.sort_cmp_passed = True
                return -1 if a < b else 1 if a > b else 0

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_cmp_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)

    def test_filter_sort_key_action_fold(test_self):
        class T(DoK):
            def filter(self, chosen: Any, arg) -> bool:
                arg.filter_passed = True
                return chosen % 2 == 0

            def sort_key(self, chosen: Any, arg):
                arg.sort_key_passed = True
                return chosen

            def action(self, chosen: Any, arg) -> Any:
                arg.action_passed = True
                return chosen + 1

            def fold(self, results: List, arg) -> Any:
                arg.fold_passed = True
                test_self.assertListEqual(
                    results,
                    sorted([i + 1 for i in test_self.elements if i % 2 == 0])[
                        : test_self.k
                    ],
                )
                return sum(results)

        arg = ArgCheck()
        inst = T()
        result = inst(test_self.k, test_self.elements, arg)
        expected_results = sum(
            sorted([i + 1 for i in test_self.elements if i % 2 == 0])[: test_self.k]
        )
        test_self.assertTrue(result == expected_results)
        test_self.assertTrue(arg.filter_passed)
        test_self.assertTrue(arg.sort_key_passed)
        test_self.assertTrue(arg.action_passed)
        test_self.assertTrue(arg.fold_passed)


if __name__ == "__main__":
    unittest.main()
