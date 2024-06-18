import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from pycontroller import Do


class Test(unittest.TestCase):
    def test_basic(self):
        def pre_controller_no_args(cls, arg1):
            cls.pre_controller_passed = arg1

        class BasicDo(Do):
            pre_controller_passed = False
            post_controller_passed = False
            pre_controller = pre_controller_no_args
            action = staticmethod(lambda: 1)
            post_controller = lambda self: self.set_post_controller_value(True)

            def set_post_controller_value(self, value: bool):
                self.post_controller_passed = value

        inst = BasicDo()
        result = inst(True)
        self.assertTrue(inst.pre_controller_passed)
        self.assertTrue(result == 1)
        self.assertTrue(inst.post_controller_passed)


if __name__ == "__main__":
    unittest.main()
