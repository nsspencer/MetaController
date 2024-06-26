import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import DoOne


class TestDoOneSmoke(unittest.TestCase):
    def test_basic(self):
        class BasicDoOne(DoOne):
            def __init__(self):
                self.pre_controller_passed = False
                self.filter_passed = False
                self.sort_key_passed = False
                self.action_passed = False
                self.post_controller_passed = False

            def pre_controller(self, arg1) -> None:
                self.pre_controller_passed = arg1

            def filter(self, chosen) -> bool:
                self.filter_passed = True
                return True

            def sort_key(self, chosen):
                self.sort_key_passed = True
                return chosen

            def action(self, chosen, arg1: bool):
                self.action_passed = arg1
                return chosen

            def post_controller(self, arg1) -> None:
                self.post_controller_passed = arg1

        inst = BasicDoOne()
        elements = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]
        result = inst(elements, True)
        self.assertTrue(result == 0)
        self.assertTrue(inst.pre_controller_passed)
        self.assertTrue(inst.filter_passed)
        self.assertTrue(inst.sort_key_passed)
        self.assertTrue(inst.action_passed)
        self.assertTrue(inst.post_controller_passed)


if __name__ == "__main__":
    unittest.main()
