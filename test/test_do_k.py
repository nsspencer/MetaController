import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(100)]


class TestDoK(unittest.TestCase):
    def test_fixed_do_k_action(self):
        class T(C):
            fixed_max_chosen = 1

            def action(self, chosen: Any) -> Any:
                return chosen

        inst = T()
        self.assertTrue(len(inst(elements)) == 1)

    def test_fixed_do_k_filter(self):
        class T(C):
            fixed_max_chosen = 1

            def filter(self, chosen: Any) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(len(inst(elements)) == 1)

    def test_fixed_do_k_preference(self):
        class T(C):
            fixed_max_chosen = 1

            def preference_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(len(inst(elements)) == 1)

    def test_fixed_do_k_empty(self):
        class T(C):
            fixed_max_chosen = 1

        inst = T()
        self.assertTrue(len(inst(elements)) == 1)

    def test_dynamic_do_k_action(self):
        class T(C):
            dynamic_max_chosen = True

            def action(self, chosen: Any) -> Any:
                return chosen

        inst = T()
        self.assertTrue(len(inst(1, elements)) == 1)

    def test_dynamic_do_k_filter(self):
        class T(C):
            dynamic_max_chosen = True

            def filter(self, chosen: Any) -> bool:
                return chosen % 2 == 0

        inst = T()
        self.assertTrue(len(inst(1, elements)) == 1)

    def test_dynamic_do_k_preference(self):
        class T(C):
            dynamic_max_chosen = True

            def preference_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        self.assertTrue(len(inst(1, elements)) == 1)

    def test_dynamic_do_k_empty(self):
        class T(C):
            dynamic_max_chosen = True

        inst = T()
        self.assertTrue(len(inst(1, elements)) == 1)

    def test_invalid_fixed_max_chosen(self):
        with self.assertRaises(ValueError):

            class T(C):
                fixed_max_chosen = 1
                dynamic_max_chosen = True


if __name__ == "__main__":
    unittest.main()
