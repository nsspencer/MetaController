import random
import unittest
from dataclasses import dataclass
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller


@dataclass
class Value:
    val: Any


elements = [random.randint(0, 100000) for _ in range(1000)]


class TestValidSimpleControllers(unittest.TestCase):
    def test_t(self):
        pass


class TestInvalidSimpleControllers(unittest.TestCase):
    def test_no_controllers(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                pass

    def test_no_partition_provided(self):
        class Test(Controller):
            def action(self, chosen: int):
                return chosen + 1

        inst = Test()
        with self.assertRaises(TypeError):
            inst()

    def test_invalid_action_arguments(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                def action(self):
                    return None

    def test_invalid_filter_arguments(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                def action(self, chosen):
                    return None

                def filter(self):
                    return True

    def test_invalid_preference_arguments_1(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                def action(self, chosen):
                    return None

                def preference(self):
                    return True

    def test_invalid_preference_arguments_2(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                def action(self, chosen):
                    return None

                def preference(self, a):
                    return True


if __name__ == "__main__":
    unittest.main()
