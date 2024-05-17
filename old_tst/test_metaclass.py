import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller
from pycontroller.controller import MetaController


class TestMetaclass(unittest.TestCase):
    def test_code_generation(self):
        class Test(Controller):
            def action(self, chosen: int):
                return chosen

        code = MetaController.generate_call_method(Test)
        self.assertTrue(callable(code))

    def test_code_compilation(self):
        code = "fn = lambda x : x + 1"
        namespace = MetaController._compile_fn(code)
        self.assertTrue(isinstance(namespace, dict))
        self.assertTrue("fn" in namespace)
        self.assertTrue(namespace["fn"](1) == 2)


if __name__ == "__main__":
    unittest.main()
