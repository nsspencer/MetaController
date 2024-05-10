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
        self.fail()

    def test_static_action_no_return(self):
        self.fail()

    def test_static_action_member_others(self):
        self.fail()

    def test_static_filter_member_others(self):
        self.fail()

    def test_static_preference_member_others(self):
        self.fail()

    def test_static_all_return(self):
        self.fail()

    def test_static_all_no_return(self):
        self.fail()


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
