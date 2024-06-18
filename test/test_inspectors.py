import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from pycontroller import Do


class Test(unittest.TestCase):
    def test_basic(self):
        def pre_controller_no_args(cls):
            cls.pre_controller_passed = True

        class BasicDo(Do):
            pre_controller_passed = False
            pre_controller = pre_controller_no_args

        inst = BasicDo()
        inst()
        self.assertTrue(inst.pre_controller_passed)


if __name__ == "__main__":
    unittest.main()
