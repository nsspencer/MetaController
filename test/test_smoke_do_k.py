import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontrollers import DoK


class TestDoKSmoke(unittest.TestCase):
    def test_basic(test_self):
        class BasicDoK(DoK):
            def __init__(self):
                self.pre_controller_passed = False
                self.filter_passed = False
                self.sort_key_passed = False
                self.action_passed = False
                self.fold_passed = False
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

            def fold(self, results: list) -> int:
                self.fold_passed = True
                test_self.assertTrue(len(results)) == 5
                return sum(results)

            def post_controller(self, arg1) -> None:
                self.post_controller_passed = arg1

        inst = BasicDoK()
        elements = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]
        result = inst(5, elements, True)
        test_self.assertTrue(result == sum(sorted(elements)[:5]))
        test_self.assertTrue(inst.pre_controller_passed)
        test_self.assertTrue(inst.filter_passed)
        test_self.assertTrue(inst.sort_key_passed)
        test_self.assertTrue(inst.action_passed)
        test_self.assertTrue(inst.fold_passed)
        test_self.assertTrue(inst.post_controller_passed)


if __name__ == "__main__":
    unittest.main()
