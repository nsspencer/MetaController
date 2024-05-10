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
    def test_do_one_normal(self):
        val = [Value(1), Value(2)]

        class DoOne(Controller):
            max_chosen = 1

            def action(self, chosen: Value):
                return chosen

            def preference(self, a, b):
                return -1 if a.val < b.val else 1 if a.val > b.val else 0

        inst = DoOne()
        self.assertEqual(inst(val)[0].val, 1)

    def test_do_one_reversed(self):
        val = [Value(1), Value(2)]

        class DoOne(Controller):
            max_chosen = 1
            reverse_sort = True

            def action(self, chosen: Value):
                return chosen

            def preference(self, a, b):
                return -1 if a.val < b.val else 1 if a.val > b.val else 0

        inst = DoOne()
        self.assertEqual(inst(val)[0].val, 2)

    def test_do_one_check_reverse_and_inverted_preference(self):
        val = [Value(1), Value(2)]

        class DoOne(Controller):
            max_chosen = 1

            def action(self, chosen: Value):
                return chosen

            def preference(self, a, b):
                return -1 if a.val < b.val else 1 if a.val > b.val else 0

        class DoOneReversed(Controller):
            max_chosen = 1
            reverse_sort = True

            def action(self, chosen: Value):
                return chosen

            def preference(self, a, b):
                return 1 if a.val < b.val else -1 if a.val > b.val else 0

        inst = DoOne()
        inst2 = DoOneReversed()
        self.assertEqual(inst(val)[0].val, inst2(val)[0].val)

    def test_max_chosen_out_of_bounds(self):
        class OutOfBounds(Controller):
            max_chosen = len(elements) + 5

            def action(self, chosen):
                return chosen

            def preference(self, a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = OutOfBounds()
        self.assertTrue(len(inst(elements)) == len(elements))

    def test_max_chosen_out_of_bounds_reversed(self):
        class OutOfBounds(Controller):
            reverse_sort = True
            max_chosen = len(elements) + 5

            def action(self, chosen):
                return chosen

            def preference(self, a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = OutOfBounds()
        self.assertTrue(len(inst(elements)) == len(elements))

    def test_no_chosen(self):
        class NoChosen(Controller):
            def action(self, chosen):
                return chosen

            def filter(self, chosen):
                return False

        inst = NoChosen()
        self.assertTrue(len(inst(elements)) == 0)

    def test_no_chosen_with_preference(self):
        class NoChosen(Controller):
            def action(self, chosen):
                return chosen

            def filter(self, chosen):
                return False

            def preference(self, a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = NoChosen()
        self.assertTrue(len(inst(elements)) == 0)

    def test_max_chosen_no_preference(self):
        class NoPrefMaxChosen(Controller):
            max_chosen = 1

            def action(self, chosen):
                return chosen

        inst = NoPrefMaxChosen()
        self.assertTrue(len(inst(elements)) == 1)

    def test_max_chosen_no_preference_out_of_bounds(self):
        class NoPrefMaxChosen(Controller):
            max_chosen = len(elements) + 100

            def action(self, chosen):
                return chosen

        inst = NoPrefMaxChosen()
        self.assertTrue(len(inst(elements)) == len(elements))


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

    def test_invalid_max_chosen_float(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                max_chosen = float(1)

    def test_invalid_max_chosen_int(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                max_chosen = 0

    def test_sort_without_preference(self):
        with self.assertRaises(AttributeError):

            class Test(Controller):
                reverse_sort = True

                def action(self, chosen):
                    return chosen


if __name__ == "__main__":
    unittest.main()
