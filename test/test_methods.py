import random

random.seed(0)
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from pycontroller import Do, DoAll, DoK, DoOne
from pycontroller.internal.exceptions import InvalidControllerMethodError


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


if __name__ == "__main__":
    unittest.main()
