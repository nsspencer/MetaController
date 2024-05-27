import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(100)]


class InvalidTests(unittest.TestCase):
    def test_invalid_action_args(self):
        with self.assertRaises(AttributeError):

            class T(C):
                def action(self):
                    return None

    def test_invalid_preference_args_1(self):
        with self.assertRaises(AttributeError):

            class T(C):
                def preference_cmp(self, a):
                    return None

    def test_invalid_preference_args_2(self):
        with self.assertRaises(AttributeError):

            class T(C):
                def preference_cmp(self):
                    return None

    def test_invalid_filter_args(self):
        with self.assertRaises(AttributeError):

            class T(C):
                def filter(self):
                    return None


if __name__ == "__main__":
    unittest.main()
