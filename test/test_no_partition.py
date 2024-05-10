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


class NoPartitionValidTests(unittest.TestCase):
    def test_no_partition_no_return(self):
        class Test(Controller):
            no_partition = True

            def action(self, val1: Value):
                val1.val += 1

        inst = Test()
        val = Value(1)
        inst(val)
        self.assertTrue(val.val == 2)

    def test_no_partition_with_return(self):
        class Test(Controller):
            no_partition = True

            def action(self, val1: int):
                return val1 + 1

        inst = Test()
        self.assertTrue(inst(1) == 2)


class NoPartitionInvalidTests(unittest.TestCase):
    def test_no_action(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                no_partition = True

    def test_with_filter(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                no_partition = True

                def filter(self, chosen: int):
                    return True

    def test_with_preference(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                no_partition = True

                def preference(self, a: int, b: int):
                    return 1

    def test_with_max_chosen(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                no_partition = True
                max_chosen = 1

                def action(self):
                    pass

    def test_with_use_simple_sort(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                no_partition = True
                use_simple_sort = True

                def action(self):
                    pass

    def test_with_reverse_sort(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                no_partition = True
                reverse_sort = True

                def action(self):
                    pass

    def test_with_return_generator(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                no_partition = True
                return_generator = True

                def action(self):
                    pass


if __name__ == "__main__":
    unittest.main()
