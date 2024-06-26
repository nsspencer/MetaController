import random
from typing import Any, List

random.seed(0)
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import Do, DoAll, DoK, DoOne
from metacontroller.internal.exceptions import InvalidControllerMethodError


class ArgWrapper:
    def __init__(self, value):
        self.value = value


class TestPreController(unittest.TestCase):
    def test_do(self):
        class T(Do):
            passed = False

            def pre_controller(self) -> None:
                self.passed = True

        inst = T()
        inst()
        self.assertTrue(inst.passed)

    def test_do_one(self):
        class T(DoOne):
            passed = False

            def pre_controller(self) -> None:
                self.passed = True

        inst = T()
        inst([])
        self.assertTrue(inst.passed)

    def test_do_k(self):
        class T(DoK):
            passed = False

            def pre_controller(self) -> None:
                self.passed = True

        inst = T()
        inst(0, [])
        self.assertTrue(inst.passed)

    def test_do_all(self):
        class T(DoAll):
            passed = False

            def pre_controller(self) -> None:
                self.passed = True

        inst = T()
        inst([])
        self.assertTrue(inst.passed)

    # static method tests
    def test_do_static(self):
        class T(Do):
            @staticmethod
            def pre_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst(arg)
        self.assertTrue(arg.value)

    def test_do_one_static(self):
        class T(DoOne):
            @staticmethod
            def pre_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst([], arg)
        self.assertTrue(arg.value)

    def test_do_k_static(self):
        class T(DoK):
            @staticmethod
            def pre_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst(0, [], arg)
        self.assertTrue(arg.value)

    def test_do_all_static(self):
        class T(DoAll):
            @staticmethod
            def pre_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst([], arg)
        self.assertTrue(arg.value)


class TestFilter(unittest.TestCase):
    def test_do(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                def filter(self, chosen) -> bool:
                    return chosen % 2 == 0

    def test_do_one(self):
        class T(DoOne):
            def filter(self, chosen) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(inst(range(10)) == 0)

    def test_do_k(self):
        class T(DoK):
            def filter(self, chosen) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(inst(3, range(10)) == [0, 2, 4])

    def test_do_all(self):
        class T(DoAll):
            def filter(self, chosen) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(inst(range(10)) == [0, 2, 4, 6, 8])

    def test_do_one_static(self):
        class T(DoOne):
            @staticmethod
            def filter(chosen) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(inst(range(10)) == 0)

    def test_do_k_static(self):
        class T(DoK):
            @staticmethod
            def filter(chosen) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(inst(3, range(10)) == [0, 2, 4])

    def test_do_all_static(self):
        class T(DoAll):
            @staticmethod
            def filter(chosen) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(inst(range(10)) == [0, 2, 4, 6, 8])


class TestSortKey(unittest.TestCase):

    def setUp(self):
        self.elements = [random.randint(0, 1000) for _ in range(10)]

    def test_do(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                def sort_key(self, chosen) -> int:
                    return chosen

    def test_do_one(self):
        class T(DoOne):
            def sort_key(self, chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(inst(self.elements) == min(self.elements))

    def test_do_k(self):
        class T(DoK):
            def sort_key(self, chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(
            inst(3, self.elements) == sorted(self.elements, key=lambda x: x)[:3]
        )

    def test_do_all(self):
        class T(DoAll):
            def sort_key(self, chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(inst(self.elements) == sorted(self.elements, key=lambda x: x))

    def test_do_one_static(self):
        class T(DoOne):
            @staticmethod
            def sort_key(chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(inst(self.elements) == min(self.elements))

    def test_do_k_static(self):
        class T(DoK):
            @staticmethod
            def sort_key(chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(
            inst(3, self.elements) == sorted(self.elements, key=lambda x: x)[:3]
        )

    def test_do_all_static(self):
        class T(DoAll):
            @staticmethod
            def sort_key(chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(inst(self.elements) == sorted(self.elements, key=lambda x: x))

    # reverse tests
    def test_do_reverse(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                reverse_sort = True

                def sort_key(self, chosen) -> int:
                    return chosen

    def test_do_one_reverse(self):
        class T(DoOne):
            reverse_sort = True

            def sort_key(self, chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(inst(self.elements) == max(self.elements))

    def test_do_k_reverse(self):
        class T(DoK):
            reverse_sort = True

            def sort_key(self, chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(
            inst(3, self.elements)
            == sorted(self.elements, key=lambda x: x, reverse=True)[:3]
        )

    def test_do_all_reverse(self):
        class T(DoAll):
            reverse_sort = True

            def sort_key(self, chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(
            inst(self.elements) == sorted(self.elements, key=lambda x: x, reverse=True)
        )

    def test_do_one_static_reverse(self):
        class T(DoOne):
            reverse_sort = True

            @staticmethod
            def sort_key(chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(inst(self.elements) == max(self.elements))

    def test_do_k_static_reverse(self):
        class T(DoK):
            reverse_sort = True

            @staticmethod
            def sort_key(chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(
            inst(3, self.elements)
            == sorted(self.elements, key=lambda x: x, reverse=True)[:3]
        )

    def test_do_all_static_reverse(self):
        class T(DoAll):
            reverse_sort = True

            @staticmethod
            def sort_key(chosen) -> int:
                return chosen

        inst = T()
        self.assertTrue(
            inst(self.elements) == sorted(self.elements, key=lambda x: x, reverse=True)
        )


class TestSortCmp(unittest.TestCase):

    def setUp(self):
        self.elements = [random.randint(0, 1000) for _ in range(10)]

    def test_do(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                def sort_cmp(self, a, b) -> int:
                    return -1 if a < b else 1 if a > b else 0

    def test_do_one(self):
        class T(DoOne):
            def sort_cmp(self, a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(inst(self.elements) == min(self.elements))

    def test_do_k(self):
        class T(DoK):
            def sort_cmp(self, a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(
            inst(3, self.elements) == sorted(self.elements, key=lambda x: x)[:3]
        )

    def test_do_all(self):
        class T(DoAll):
            def sort_cmp(self, a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(inst(self.elements) == sorted(self.elements, key=lambda x: x))

    def test_do_one_static(self):
        class T(DoOne):
            @staticmethod
            def sort_cmp(a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(inst(self.elements) == min(self.elements))

    def test_do_k_static(self):
        class T(DoK):
            @staticmethod
            def sort_cmp(a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(
            inst(3, self.elements) == sorted(self.elements, key=lambda x: x)[:3]
        )

    def test_do_all_static(self):
        class T(DoAll):
            @staticmethod
            def sort_cmp(a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(inst(self.elements) == sorted(self.elements, key=lambda x: x))

    # reverse tests
    def test_do_reverse(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                reverse_sort = True

                def sort_cmp(self, a, b) -> int:
                    return -1 if a < b else 1 if a > b else 0

    def test_do_one_reverse(self):
        class T(DoOne):
            reverse_sort = True

            def sort_cmp(self, a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(inst(self.elements) == max(self.elements))

    def test_do_k_reverse(self):
        class T(DoK):
            reverse_sort = True

            def sort_cmp(self, a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(
            inst(3, self.elements)
            == sorted(self.elements, key=lambda x: x, reverse=True)[:3]
        )

    def test_do_all_reverse(self):
        class T(DoAll):
            reverse_sort = True

            def sort_cmp(self, a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(
            inst(self.elements) == sorted(self.elements, key=lambda x: x, reverse=True)
        )

    def test_do_one_static_reverse(self):
        class T(DoOne):
            reverse_sort = True

            @staticmethod
            def sort_cmp(a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(inst(self.elements) == max(self.elements))

    def test_do_k_static_reverse(self):
        class T(DoK):
            reverse_sort = True

            @staticmethod
            def sort_cmp(a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(
            inst(3, self.elements)
            == sorted(self.elements, key=lambda x: x, reverse=True)[:3]
        )

    def test_do_all_static_reverse(self):
        class T(DoAll):
            reverse_sort = True

            @staticmethod
            def sort_cmp(a, b) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(
            inst(self.elements) == sorted(self.elements, key=lambda x: x, reverse=True)
        )


class TestAction(unittest.TestCase):
    def setUp(self):
        self.elements = [random.randint(0, 1000) for _ in range(10)]

    def test_do_no_return(self):
        self.passed = False

        class T(Do):
            def action(do_self):
                self.passed = True

        inst = T()
        inst()
        self.assertTrue(self.passed)

    def test_do_one_no_return(self):
        self.passed = False
        self.count = 0

        class T(DoOne):
            def action(do_self, chosen):
                self.passed = True
                self.count += 1

        inst = T()
        inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == 1)

    def test_do_k_no_return(self):
        self.passed = False
        self.count = 0

        class T(DoK):
            def action(do_self, chosen):
                self.passed = True
                self.count += 1

        k = 5
        inst = T()
        inst(k, self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == 5)

    def test_do_all_no_return(self):
        self.passed = False
        self.count = 0

        class T(DoAll):
            def action(do_self, chosen):
                self.passed = True
                self.count += 1

        inst = T()
        inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == len(self.elements))

    # with return
    def test_do_return(self):
        self.passed = False

        class T(Do):
            def action(do_self):
                self.passed = True
                return True

        inst = T()
        result = inst()
        self.assertTrue(self.passed)
        self.assertTrue(result)

    def test_do_one_return(self):
        self.passed = False
        self.count = 0

        class T(DoOne):
            def action(do_self, chosen):
                self.passed = True
                self.count += 1
                return chosen

        inst = T()
        result = inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == 1)
        self.assertTrue(result == self.elements[0])

    def test_do_k_return(self):
        self.passed = False
        self.count = 0

        class T(DoK):
            def action(do_self, chosen):
                self.passed = True
                self.count += 1
                return chosen

        k = 5
        inst = T()
        result = inst(k, self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == k)
        self.assertTrue(result == self.elements[:k])

    def test_do_all_return(self):
        self.passed = False
        self.count = 0

        class T(DoAll):
            def action(do_self, chosen):
                self.passed = True
                self.count += 1
                return chosen

        inst = T()
        result = inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == len(self.elements))
        self.assertTrue(result == self.elements)

    # static tests
    def test_do_no_return_static(self):
        self.passed = False

        class T(Do):
            @staticmethod
            def action():
                self.passed = True

        inst = T()
        inst()
        self.assertTrue(self.passed)

    def test_do_one_no_return_static(self):
        self.passed = False
        self.count = 0

        class T(DoOne):
            @staticmethod
            def action(chosen):
                self.passed = True
                self.count += 1

        inst = T()
        inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == 1)

    def test_do_k_no_return_static(self):
        self.passed = False
        self.count = 0

        class T(DoK):
            @staticmethod
            def action(chosen):
                self.passed = True
                self.count += 1

        k = 5
        inst = T()
        inst(k, self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == 5)

    def test_do_all_no_return_static(self):
        self.passed = False
        self.count = 0

        class T(DoAll):
            @staticmethod
            def action(chosen):
                self.passed = True
                self.count += 1

        inst = T()
        inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == len(self.elements))

    # with return
    def test_do_return_static(self):
        self.passed = False

        class T(Do):
            @staticmethod
            def action():
                self.passed = True
                return True

        inst = T()
        result = inst()
        self.assertTrue(self.passed)
        self.assertTrue(result)

    def test_do_one_return_static(self):
        self.passed = False
        self.count = 0

        class T(DoOne):
            @staticmethod
            def action(chosen):
                self.passed = True
                self.count += 1
                return chosen

        inst = T()
        result = inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == 1)
        self.assertTrue(result == self.elements[0])

    def test_do_k_return_static(self):
        self.passed = False
        self.count = 0

        class T(DoK):
            @staticmethod
            def action(chosen):
                self.passed = True
                self.count += 1
                return chosen

        k = 5
        inst = T()
        result = inst(k, self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == k)
        self.assertTrue(result == self.elements[:k])

    def test_do_all_return_static(self):
        self.passed = False
        self.count = 0

        class T(DoAll):
            @staticmethod
            def action(chosen):
                self.passed = True
                self.count += 1
                return chosen

        inst = T()
        result = inst(self.elements)
        self.assertTrue(self.passed)
        self.assertTrue(self.count == len(self.elements))
        self.assertTrue(result == self.elements)


class TestFold(unittest.TestCase):
    def test_do(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                def fold(self, results):
                    return 0

    def test_do_one(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(DoOne):
                def fold(self, results):
                    return 0

    def test_do_k(self):
        class T(DoK):
            def fold(self, results: List):
                return sum(results)

        inst = T()
        elements = [random.randint(0, 1000) for _ in range(10)]
        result = inst(5, elements)
        self.assertTrue(sum(elements[:5]) == result)

    def test_do_all(self):
        class T(DoAll):
            def fold(self, results: List):
                return sum(results)

        inst = T()
        elements = [random.randint(0, 1000) for _ in range(10)]
        result = inst(elements)
        self.assertTrue(sum(elements) == result)

    # staticmethods
    def test_do_static(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(Do):
                @staticmethod
                def fold(results):
                    return 0

    def test_do_one_static(self):
        with self.assertRaises(InvalidControllerMethodError):

            class T(DoOne):
                @staticmethod
                def fold(results):
                    return 0

    def test_do_k_static(self):
        class T(DoK):
            @staticmethod
            def fold(results: List):
                return sum(results)

        inst = T()
        elements = [random.randint(0, 1000) for _ in range(10)]
        result = inst(5, elements)
        self.assertTrue(sum(elements[:5]) == result)

    def test_do_all_static(self):
        class T(DoAll):
            @staticmethod
            def fold(results: List):
                return sum(results)

        inst = T()
        elements = [random.randint(0, 1000) for _ in range(10)]
        result = inst(elements)
        self.assertTrue(sum(elements) == result)


class TestPostController(unittest.TestCase):
    def test_do(self):
        class T(Do):
            passed = False

            def post_controller(self) -> None:
                self.passed = True

        inst = T()
        inst()
        self.assertTrue(inst.passed)

    def test_do_one(self):
        class T(DoOne):
            passed = False

            def post_controller(self) -> None:
                self.passed = True

        inst = T()
        inst([])
        self.assertTrue(inst.passed)

    def test_do_k(self):
        class T(DoK):
            passed = False

            def post_controller(self) -> None:
                self.passed = True

        inst = T()
        inst(0, [])
        self.assertTrue(inst.passed)

    def test_do_all(self):
        class T(DoAll):
            passed = False

            def post_controller(self) -> None:
                self.passed = True

        inst = T()
        inst([])
        self.assertTrue(inst.passed)

    # static method tests
    def test_do_static(self):
        class T(Do):
            @staticmethod
            def post_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst(arg)
        self.assertTrue(arg.value)

    def test_do_one_static(self):
        class T(DoOne):
            @staticmethod
            def post_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst([], arg)
        self.assertTrue(arg.value)

    def test_do_k_static(self):
        class T(DoK):
            @staticmethod
            def post_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst(0, [], arg)
        self.assertTrue(arg.value)

    def test_do_all_static(self):
        class T(DoAll):
            @staticmethod
            def post_controller(arg1) -> None:
                arg1.value = True

        inst = T()
        arg = ArgWrapper(False)
        inst([], arg)
        self.assertTrue(arg.value)


if __name__ == "__main__":
    unittest.main()
