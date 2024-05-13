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


class NoPartitionStaticsTests(unittest.TestCase):
    def test_no_return_static_action(self):
        class Test(Controller):
            no_partition = True

            @staticmethod
            def action(val1: Value):
                val1.val += 1

        inst = Test()
        val = Value(1)
        inst(val)
        self.assertTrue(val.val == 2)

    def test_with_return_static_action(self):
        class Test(Controller):
            no_partition = True

            @staticmethod
            def action(val1: int):
                return val1 + 1

        inst = Test()
        self.assertTrue(inst(1) == 2)

    def test_no_return_static_action_static_mode(self):
        class Test(Controller):
            no_partition = True
            static_mode = True

            @staticmethod
            def action(val1: Value):
                val1.val += 1

        val = Value(1)
        Test(val)
        self.assertTrue(val.val == 2)

    def test_with_return_static_action_static_mode(self):
        class Test(Controller):
            no_partition = True
            static_mode = True

            @staticmethod
            def action(val1: int):
                return val1 + 1

        self.assertTrue(Test(1) == 2)


class ValidStaticMethodTests(unittest.TestCase):
    def test_static_action_return(self):
        class Test(Controller):
            @staticmethod
            def action(chosen):
                return chosen

        inst = Test()
        self.assertTrue(len(inst(elements)) == len(elements))

    def test_static_action_no_return(self):
        class Test(Controller):
            @staticmethod
            def action(chosen):
                chosen.val += 1

        local_elements = [Value(i) for i in range(1000)]
        original_sum = sum([i.val for i in local_elements])
        inst = Test()
        inst(local_elements)
        new_sum = sum([i.val for i in local_elements])
        self.assertTrue(new_sum == original_sum + len(local_elements))

    def test_static_action_member_others(self):
        class Test(Controller):
            @staticmethod
            def action(chosen):
                chosen.val = -1

            def filter(self, chosen: Value):
                return chosen.val % 2 == 0

            def preference(self, a, b):
                return -1 if a.val < b.val else 1 if a.val > b.val else 0

        local_vals = [Value(i) for i in range(1000)]
        answer = sum([-1 for i in local_vals if i.val % 2 == 0])
        inst = Test()
        inst(local_vals)
        found_answer = sum([i.val for i in local_vals if i.val == -1])
        self.assertTrue(answer == found_answer)

    def test_static_filter_member_others(self):
        class Test(Controller):
            def action(self, chosen):
                return chosen

            @staticmethod
            def filter(chosen):
                return chosen % 2 == 0

            def preference(self, a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = Test()
        expected_answer = sum([i for i in elements if i % 2 == 0])
        self.assertTrue(sum(inst(elements)) == expected_answer)

    def test_static_preference_member_others(self):
        class Test(Controller):
            def action(self, chosen):
                return chosen

            def filter(self, chosen):
                return chosen % 2 == 0

            @staticmethod
            def preference(a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = Test()
        expected_answer = sum([i for i in elements if i % 2 == 0])
        self.assertTrue(sum(inst(elements)) == expected_answer)

    def test_static_all_no_return(self):
        class Test(Controller):
            @staticmethod
            def action(chosen):
                chosen.val = -1

            @staticmethod
            def filter(chosen: Value):
                return chosen.val % 2 == 0

            @staticmethod
            def preference(a, b):
                return -1 if a.val < b.val else 1 if a.val > b.val else 0

        local_vals = [Value(i) for i in range(1000)]
        answer = sum([-1 for i in local_vals if i.val % 2 == 0])
        inst = Test()
        inst(local_vals)
        found_answer = sum([i.val for i in local_vals if i.val == -1])
        self.assertEqual(answer, found_answer)

    def test_static_all_return(self):
        class Test(Controller):
            @staticmethod
            def action(chosen):
                return chosen

            @staticmethod
            def filter(chosen: Value):
                return chosen.val % 2 == 0

            @staticmethod
            def preference(a, b):
                return -1 if a.val < b.val else 1 if a.val > b.val else 0

        local_vals = [Value(i) for i in range(1000)]
        answer = sum([i.val for i in local_vals if i.val % 2 == 0])
        inst = Test()
        found_answer = sum([i.val for i in inst(local_vals)])
        self.assertEqual(answer, found_answer)

    def test_static_max_chosen(self):
        class Test(Controller):
            max_chosen = 1

            @staticmethod
            def action(chosen):
                return chosen

        inst = Test()
        self.assertEqual(len(inst(elements)), 1)

    def test_static_max_chosen_with_preference(self):
        class Test(Controller):
            max_chosen = 1

            @staticmethod
            def action(chosen):
                return chosen

            @staticmethod
            def preference(a, b):
                return -1 if a < b else 1 if a > b else 0

        inst = Test()
        self.assertEqual(len(inst(elements)), 1)

    def test_static_mode_max_chosen_with_preference(self):
        class Test(Controller):
            max_chosen = 1
            static_mode = True

            @staticmethod
            def action(chosen):
                return chosen

            @staticmethod
            def preference(a, b):
                return -1 if a < b else 1 if a > b else 0

        self.assertEqual(len(Test(elements)), 1)

    def test_static_mode_max_chosen_with_filter_out_of_bounds(self):
        class Test(Controller):
            max_chosen = len(elements) + 1000
            static_mode = True

            @staticmethod
            def action(chosen):
                return chosen

            @staticmethod
            def filter(chosen):
                return True

        self.assertEqual(len(Test(elements)), len(elements))


class InvalidStaticsTests(unittest.TestCase):
    def test_invalid_args_static_mode(self):
        class Test(Controller):
            static_mode = True

            def action(bad_self, value):
                pass

        with self.assertRaises(TypeError):
            Test(1)

    def test_invalid_action_args_static_method(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                @staticmethod
                def action():
                    pass

    def test_invalid_filter_args_static_method(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                @staticmethod
                def filter():
                    return True

    def test_invalid_preference_args_static_method(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                @staticmethod
                def preference():
                    return True

    def test_invalid_preference_args_static_method_2(self):
        with self.assertRaises(TypeError):

            class Test(Controller):
                @staticmethod
                def preference(a):
                    return True


if __name__ == "__main__":
    unittest.main()
