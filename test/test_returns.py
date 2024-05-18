import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(100)]


class TestReturnTypes(unittest.TestCase):
    def test_action(self):
        class T(C):
            def action(self, chosen: Any) -> Any:
                return chosen

        i = T()
        result = i(elements)
        self.assertTrue(isinstance(result, list))

    def test_filter(self):
        class T(C):
            def filter(self, chosen: Any) -> Any:
                return True

        i = T()
        result = i(elements)
        self.assertTrue(isinstance(result, list))

    def test_preference(self):
        class T(C):
            def preference(self, a, b) -> Any:
                return -1

        i = T()
        result = i(elements)
        self.assertTrue(isinstance(result, list))

    def test_action_arg(self):
        class T(C):
            def action(self, chosen: Any, arg: int) -> Any:
                return chosen + arg

        i = T()
        result = i(elements, 1)
        self.assertTrue(isinstance(result, list))

    def test_filter_arg(self):
        class T(C):
            def filter(self, chosen: Any, arg: int) -> Any:
                return bool(arg)

        i = T()
        result = i(elements, 1)
        self.assertTrue(isinstance(result, list))

    def test_preference_arg(self):
        class T(C):
            def preference(self, a, b, arg: int) -> Any:
                arg.val += 1
                return -1 if a < b else 1 if a > b else 0

        i = T()

        class ArgClass:
            def __init__(self, val) -> None:
                self.val = val

        arg = ArgClass(0)
        result = i(elements, arg)
        self.assertTrue(isinstance(result, list))

    def test_empty(self):
        class T(C): ...

        i = T()
        result = i(elements)
        self.assertTrue(isinstance(result, type(elements)))


if __name__ == "__main__":
    unittest.main()
