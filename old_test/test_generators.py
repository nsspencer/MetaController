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


class TestGenerators(unittest.TestCase): ...


if __name__ == "__main__":
    unittest.main()
