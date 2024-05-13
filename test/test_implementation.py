import random
import unittest

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(1000)]


class BasicImplementationTest(unittest.TestCase):
    def test_none(self):
        class T(C):
            pass

        inst = T()
        result = inst(elements)
        self.assertTrue(result == elements)

    def test_action(self):
        class T(C):
            def action(self, chosen: int) -> int:
                return chosen

        inst = T()
        result = inst(elements)
        self.assertTrue(all(result[i] == elements[i] for i in range(len(elements))))

    def test_filter(self):
        class T(C):
            def filter(self, chosen: int) -> bool:
                return chosen % 2 == 0

        inst = T()
        results = inst(elements)
        for result in results:
            self.assertTrue(result % 2 == 0)

    def test_preference(self):
        class T(C):
            def preference(self, a: int, b: int) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        results = inst(elements)
        last_result = min(elements)
        for result in results:
            self.assertTrue(result >= last_result)
            last_result = result

    def test_action_filter(self):
        class T(C):
            def action(self, chosen: int) -> int:
                return chosen + 1

            def filter(self, chosen: int) -> bool:
                return chosen % 2 == 0

        inst = T()
        results = inst(elements)
        for result in results:
            self.assertTrue(result % 2 == 1)

    def test_action_preference(self):
        class T(C):
            def action(self, chosen: int) -> int:
                return chosen + 1

            def preference(self, a: int, b: int) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        results = inst(elements)
        last_result = min(elements)
        for result in results:
            self.assertTrue(result >= last_result)
            self.assertTrue(result % 2 == 0 or result % 2 == 1)
            last_result = result

    def test_filter_preference(self):
        class T(C):
            def filter(self, chosen: int) -> bool:
                return chosen % 2 == 0

            def preference(self, a: int, b: int) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        results = inst(elements)
        last_result = min(elements)
        for result in results:
            self.assertTrue(result >= last_result)
            self.assertTrue(result % 2 == 0)
            last_result = result

    def test_action_filter_preference(self):
        class T(C):
            def action(self, chosen: int) -> int:
                return chosen + 1

            def filter(self, chosen: int) -> bool:
                return chosen % 2 == 0

            def preference(self, a: int, b: int) -> int:
                return -1 if a < b else 1 if a > b else 0

        inst = T()
        results = inst(elements)
        last_result = min(elements)
        for result in results:
            self.assertTrue(result >= last_result)
            self.assertTrue(result % 2 == 1)
            last_result = result


if __name__ == "__main__":
    unittest.main()
