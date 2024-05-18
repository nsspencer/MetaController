import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(100)]


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
                sort_with_key = True

                def preference(self, a: Any, b: Any, *args, **kwargs) -> int:
                    return super().preference(a, b, *args, **kwargs)

    def test_simple_sort(self):
        class T(C):
            sort_with_key = True

            def action(self, chosen: int) -> Any:
                return chosen

        inst = T()
        result = inst(elements)
        self.assertTrue(is_sorted(result))

    def test_invalid_reverse_sort(self):
        with self.assertRaises(ValueError):

            class T(C):
                sort_reverse = True

                def action(self, chosen: Any, *args, **kwargs) -> Any:
                    return chosen

    def test_simple_sort_reverse(self):
        class T(C):
            sort_with_key = True
            sort_reverse = True

            def action(self, chosen: int) -> Any:
                return chosen

        inst = T()
        result = inst(elements)
        self.assertTrue(is_sorted(result, reverse=True))

    def test_preference_reverse(self):
        class T(C):
            sort_reverse = True

            def action(self, chosen: int) -> Any:
                return chosen

            def preference(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        result = inst(elements)
        self.assertTrue(is_sorted(result, reverse=True))

    def test_preference_with_key_with_reverse(self):
        with self.assertRaises(ValueError):

            class T(C):
                sort_reverse = True
                sort_with_key = True

                def action(self, chosen: int) -> Any:
                    return chosen

                def preference(self, a: Any, b: Any) -> int:
                    return -1 if a < b else 1 if a > b else 0

    def test_preference_with_key_with_reverse(self):
        with self.assertRaises(ValueError):

            class T(C):
                sort_reverse = True
