import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(1000)]


def global_test_fn(value: int) -> int:
    return value + 1


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

    def test_global_calls(self):
        class T(C):
            def action(self, chosen: int) -> int:
                return global_test_fn(chosen)

        inst = T()
        results = inst(elements)
        normal_sum = sum(elements)
        new_sum = sum(results)
        self.assertTrue(normal_sum + len(elements) == new_sum)


class ActionArgumentImplementationTests(unittest.TestCase):
    def test_positional_arg(self):
        class T(C):
            def action(self, chosen: Any, pos_arg: int) -> Any:
                return chosen + pos_arg

        original_sum = sum(elements)
        a = T()
        e = a(elements, 1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 1))

    def test_keyword_arg(self):
        class T(C):
            def action(self, chosen: Any, keyword_arg: int = 0) -> Any:
                return chosen + keyword_arg

        original_sum = sum(elements)
        a = T()
        e = a(elements, keyword_arg=1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 1))

    def test_keyword_default_arg(self):
        class T(C):
            def action(self, chosen: Any, keyword_arg: int = 1) -> Any:
                return chosen + keyword_arg

        original_sum = sum(elements)
        a = T()
        e = a(elements)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 1))

    def test_positional_and_keyword_default_arg(self):
        class T(C):
            def action(self, chosen: Any, pos_arg0: int, keyword_arg: int = 1) -> Any:
                return chosen + pos_arg0 + keyword_arg

        original_sum = sum(elements)
        a = T()
        e = a(elements, 1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 2))

    def test_arg_unpack_arg(self):
        class T(C):
            def action(self, chosen: Any, *args) -> Any:
                return chosen + args[0]

        original_sum = sum(elements)
        a = T()
        e = a(elements, 1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 1))

    def test_kwarg_unpack_arg(self):
        class T(C):
            def action(self, chosen: Any, **kwargs) -> Any:
                return chosen + kwargs["keyword_argument"]

        original_sum = sum(elements)
        a = T()
        e = a(elements, keyword_argument=1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 1))

    def test_arg_and_kwarg_unpack_arg(self):
        class T(C):
            def action(self, chosen: Any, *args, **kwargs) -> Any:
                return chosen + args[0] + kwargs["keyword_argument"]

        original_sum = sum(elements)
        a = T()
        e = a(elements, 1, keyword_argument=1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 2))

    def test_positional_keyword_arg_and_kwarg_unpack_arg(self):
        class T(C):
            def action(
                self, chosen: Any, pos_arg0, *args, keyword_arg1=1, **kwargs
            ) -> Any:
                return (
                    chosen
                    + pos_arg0
                    + keyword_arg1
                    + args[0]
                    + kwargs["keyword_argument2"]
                )

        original_sum = sum(elements)
        a = T()
        e = a(elements, 1, 1, keyword_arg1=1, keyword_argument2=1)
        self.assertTrue(sum(e) == original_sum + (len(elements) * 4))


class FilterArgumentImplementationTests(unittest.TestCase):
    FIND_ME = 1

    def test_positional_arg(self):
        class T(C):
            def filter(self, chosen: Any, pos_arg: int) -> bool:
                return chosen % pos_arg == 0

        a = T()
        e = a(elements, 1)
        self.assertTrue(all([i % 1 == 0 for i in e]))

    def test_keyword_arg(self):
        class T(C):
            def filter(self, chosen: Any, keyword_arg: int = 1) -> bool:
                return chosen % keyword_arg == 0

        a = T()
        e = a(elements, keyword_arg=3)
        self.assertTrue(all([i % 3 == 0 for i in e]))

    def test_keyword_arg_default(self):
        class T(C):
            def filter(self, chosen: Any, keyword_arg: int = 1) -> bool:
                return chosen % keyword_arg == 0

        a = T()
        e = a(elements)
        self.assertTrue(all([i % 1 == 0 for i in e]))

    def test_positional_and_keyword_arg(self):
        class T(C):
            def filter(self, chosen: Any, arg0: int, keyword_arg: int = 1) -> bool:
                return chosen % arg0 == keyword_arg

        a = T()
        e = a(elements, 3, keyword_arg=1)
        self.assertTrue(all([i % 3 == 1 for i in e]))

    def test_arg_unpack(self):
        class T(C):
            def filter(self, chosen: Any, *args) -> bool:
                return chosen % args[0] == 0

        a = T()
        e = a(elements, 2)
        self.assertTrue(all([i % 2 == 0 for i in e]))

    def test_kwarg_unpack(self):
        class T(C):
            def filter(self, chosen: Any, **kwargs) -> bool:
                return chosen % kwargs["keyword_arg"] == 0

        a = T()
        e = a(elements, keyword_arg=2)
        self.assertTrue(all([i % 2 == 0 for i in e]))

    def test_arg_and_kwarg_unpack(self):
        class T(C):
            def filter(self, chosen: Any, *args, **kwargs) -> bool:
                return chosen % args[0] == kwargs["keyword_arg"]

        a = T()
        e = a(elements, 2, keyword_arg=0)
        self.assertTrue(all([i % 2 == 0 for i in e]))

    def test_positional_keyword_arg_and_kwarg_unpack_arg(self):
        class T(C):
            def filter(self, chosen: Any, arg0, *args, keyword_arg, **kwargs) -> bool:
                assert arg0 == args[0]
                assert keyword_arg == kwargs["keyword_arg2"]
                return chosen % arg0 == keyword_arg

        a = T()
        e = a(elements, 2, 2, keyword_arg=1, keyword_arg2=1)
        self.assertTrue(all([i % 2 == 1 for i in e]))


if __name__ == "__main__":
    unittest.main()
