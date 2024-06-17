import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from pycontroller2 import Do, DoAll, DoK, DoOne

TEST_GLOBAL = False


class TestDo(unittest.TestCase):
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


class TestDoOne(unittest.TestCase):
    def test_basic(self):
        class BasicDoOne(DoOne):
            def __init__(self):
                self.pre_controller_passed = False
                self.filter_passed = False
                self.preference_key_passed = False
                self.action_passed = False
                self.post_controller_passed = False

            def pre_controller(self, arg1) -> None:
                self.pre_controller_passed = arg1

            def filter(self, chosen) -> bool:
                self.filter_passed = True
                return True

            def preference_key(self, chosen):
                self.preference_key_passed = True
                return chosen

            # def preference_cmp(self, a, b, arg1) -> int:
            #     self.preference_key_passed = arg1
            #     return -1 if a < b else 1 if a > b else 0

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
        self.assertTrue(inst.preference_key_passed)
        self.assertTrue(inst.action_passed)
        self.assertTrue(inst.post_controller_passed)


class TestDoK(unittest.TestCase):
    def test_basic(test_self):
        class BasicDoK(DoK):
            def __init__(self):
                self.pre_controller_passed = False
                self.filter_passed = False
                self.preference_key_passed = False
                self.action_passed = False
                self.fold_passed = False
                self.post_controller_passed = False

            def pre_controller(self, arg1) -> None:
                self.pre_controller_passed = arg1

            def filter(self, chosen) -> bool:
                self.filter_passed = True
                return True

            # def preference_key(self, chosen):
            #     self.preference_key_passed = True
            #     return chosen

            def preference_cmp(self, a, b, arg1) -> int:
                self.preference_key_passed = arg1
                return -1 if a < b else 1 if a > b else 0

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
        test_self.assertTrue(inst.preference_key_passed)
        test_self.assertTrue(inst.action_passed)
        test_self.assertTrue(inst.fold_passed)
        test_self.assertTrue(inst.post_controller_passed)


if __name__ == "__main__":
    unittest.main()
