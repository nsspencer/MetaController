import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from pycontroller2 import Do, DoAll, DoK, DoOne

TEST_GLOBAL = None


class TestDo(unittest.TestCase):
    def test_basic_do(self):
        TEST_LOCAL = None

        class BaseDo(Do):
            def __init__(self) -> None:
                self.precontroller_passed = False
                self.postcontroller_passed = False
                self.action_passed = False

            def pre_controller(self) -> None:
                self.precontroller_passed = True

            def action(self) -> int:
                self.action_passed = True

            def post_controller(self) -> None:
                self.postcontroller_passed = True

        inst = BaseDo()

        # call the controller
        inst()
        self.assertTrue(inst.precontroller_passed)
        self.assertTrue(inst.postcontroller_passed)
        self.assertTrue(inst.action_passed)


if __name__ == "__main__":
    unittest.main()
