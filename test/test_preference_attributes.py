import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Comparable
from pycontroller import Controller as C


class Data:
    def __init__(self, value: int) -> None:
        self.value = value


elements = [random.randint(0, 1000000) for _ in range(100)]

data_elements = [Data(random.randint(0, 1000000)) for _ in range(100)]


def is_sorted(elements: list, reverse: bool = False) -> bool:
    for index, element in enumerate(elements[1:]):
        if reverse:
            if element > elements[index]:
                return False
        else:
            if element < elements[index]:
                return False
    return True


class TestPreferenceAttributes(unittest.TestCase):
    def test_is_sorted(self):
        self.assertTrue(is_sorted(sorted(elements)))
        self.assertTrue(is_sorted(sorted(elements, reverse=True), reverse=True))
        self.assertFalse(is_sorted(sorted(elements, reverse=True)))
        self.assertFalse(is_sorted(sorted(elements), reverse=True))

    def test_invalid_sort(self):
        with self.assertRaises(ValueError):

            class T(C):
                simple_sort = True

                def preference_cmp(self, a: Any, b: Any, *args, **kwargs) -> int:
                    return super().preference(a, b, *args, **kwargs)

    def test_simple_sort(self):
        class T(C):
            simple_sort = True

            def action(self, chosen: int) -> Any:
                return chosen

        inst = T()
        result = inst(elements)
        self.assertTrue(is_sorted(result))

    def test_invalid_reverse_sort(self):
        with self.assertRaises(ValueError):

            class T(C):
                reverse_sort = True

                def action(self, chosen: Any, *args, **kwargs) -> Any:
                    return chosen

    def test_simple_sort_reverse(self):
        class T(C):
            simple_sort = True
            reverse_sort = True

            def action(self, chosen: int) -> Any:
                return chosen

        inst = T()
        result = inst(elements)
        self.assertTrue(is_sorted(result, reverse=True))

    def test_preference_reverse(self):
        class T(C):
            reverse_sort = True

            def action(self, chosen: int) -> Any:
                return chosen

            def preference_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        result = inst(elements)
        self.assertTrue(is_sorted(result, reverse=True))

    def test_preference_with_key_with_reverse(self):
        with self.assertRaises(ValueError):

            class T(C):
                reverse_sort = True
                simple_sort = True

                def action(self, chosen: int) -> Any:
                    return chosen

                def preference_cmp(self, a: Any, b: Any) -> int:
                    return -1 if a < b else 1 if a > b else 0

    def test_preference_with_key_with_reverse(self):
        with self.assertRaises(ValueError):

            class T(C):
                reverse_sort = True


class TestPreferenceKey(unittest.TestCase):
    def test_simple_key(self):
        class T(C):
            def preference(self, chosen: Data):
                return chosen.value

        inst = T()
        vals = inst(data_elements)
        self.assertTrue(is_sorted([i.value for i in vals]))

    def test_simple_key_reverse(self):
        class T(C):
            reverse_sort = True

            def preference(self, chosen: Data):
                return chosen.value

        inst = T()
        vals = inst(data_elements)
        self.assertTrue(is_sorted([i.value for i in vals], reverse=True))

    def test_invalid_builtin_key_sort(self):
        class T(C):
            simple_sort = True

        inst = T()
        with self.assertRaises(TypeError):
            vals = inst(data_elements)

    def test_invalid_preference_args(self):
        with self.assertRaises(AttributeError):

            class T(C):
                def preference(self) -> Comparable:
                    return None

    def test_invalid_preference_args_static(self):
        with self.assertRaises(AttributeError):

            class T(C):
                @staticmethod
                def preference() -> Comparable:
                    return None

    def test_preference_with_args(self):
        class T(C):
            def preference(self, chosen: Data, arg1: int) -> Comparable:
                return chosen.value + arg1

        inst = T()
        vals = inst(data_elements, 0)
        self.assertTrue(is_sorted([i.value for i in vals]))

    def test_preference_with_kwargs(self):
        class T(C):
            def preference(
                self, chosen: Data, arg0: int, kwarg0: int = 1
            ) -> Comparable:
                return chosen.value + arg0 + kwarg0

        inst = T()
        vals = inst(data_elements, 0)
        self.assertTrue(is_sorted([i.value for i in vals]))
        vals = inst(data_elements, 0, kwarg0=10)
        self.assertTrue(is_sorted([i.value for i in vals]))

    def test_preference_with_args_reverse(self):
        class T(C):
            reverse_sort = True

            def preference(self, chosen: Data, arg1: int) -> Comparable:
                return chosen.value + arg1

        inst = T()
        vals = inst(data_elements, 0)
        self.assertTrue(is_sorted([i.value for i in vals], reverse=True))

    def test_preference_with_kwargs_reverse(self):
        class T(C):
            reverse_sort = True

            def preference(
                self, chosen: Data, arg0: int, kwarg0: int = 1
            ) -> Comparable:
                return chosen.value + arg0 + kwarg0

        inst = T()
        vals = inst(data_elements, 0)
        self.assertTrue(is_sorted([i.value for i in vals], reverse=True))
        vals = inst(data_elements, 0, kwarg0=10)
        self.assertTrue(is_sorted([i.value for i in vals], reverse=True))
