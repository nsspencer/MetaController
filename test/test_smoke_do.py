import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import Do

TEST_GLOBAL = False


class TestDoSmoke(unittest.TestCase):
    def test_basic_do(self):
        TEST_LOCAL = False

        class BaseDo(Do):
            def __init__(self) -> None:
                self.precontroller_passed = False
                self.postcontroller_passed = False
                self.action_passed = False

            def pre_controller(self) -> None:
                self.precontroller_passed = True

            def action(self):
                global TEST_GLOBAL
                nonlocal TEST_LOCAL
                self.action_passed = True
                TEST_LOCAL = True
                TEST_GLOBAL = True

            def post_controller(self) -> None:
                self.postcontroller_passed = True

        inst = BaseDo()

        # call the controller
        inst()
        self.assertTrue(inst.precontroller_passed)
        self.assertTrue(inst.postcontroller_passed)
        self.assertTrue(inst.action_passed)
        self.assertTrue(TEST_LOCAL)
        self.assertTrue(TEST_GLOBAL)

    def test_args_basic_do_return(test_self):

        class BaseDo(Do):
            def __init__(self) -> None:
                self.precontroller_passed = False
                self.postcontroller_passed = False
                self.action_passed = False

            def pre_controller(self, *args) -> None:
                self.precontroller_passed = True
                test_self.assertTrue(len(args) == 7)

            def action(self, arg0, **kwargs) -> int:
                self.action_passed = True
                test_self.assertTrue(arg0 == 0)
                test_self.assertTrue(kwargs.get("test", None) is not None)
                return arg0

            def post_controller(self, *args) -> None:
                self.postcontroller_passed = True
                test_self.assertTrue(len(args) == 7)

        inst = BaseDo()

        # call the controller
        result = inst(0, 1, 2, 3, 4, 5, 6, 7, test=1)
        test_self.assertTrue(inst.precontroller_passed)
        test_self.assertTrue(inst.postcontroller_passed)
        test_self.assertTrue(inst.action_passed)
        test_self.assertTrue(result == 0)

    def test_static(self):
        class StaticDo(Do):
            @staticmethod
            def action(arg0):
                return arg0 + 1

        inst = StaticDo()
        self.assertTrue(inst(0) == 1)


if __name__ == "__main__":
    unittest.main()
