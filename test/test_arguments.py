import random
import unittest
from typing import Any

random.seed(0)

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pycontroller import Controller as C

elements = [random.randint(0, 1000000) for _ in range(100)]


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
            def filter(
                self, chosen: Any, arg0, *args, keyword_arg=0, **my_kwargs
            ) -> bool:
                assert arg0 == args[0]
                assert keyword_arg == my_kwargs["keyword_arg2"]
                return chosen % arg0 == keyword_arg

        a = T()
        e = a(elements, 2, 2, keyword_arg=1, keyword_arg2=1)
        self.assertTrue(all([i % 2 == 1 for i in e]))


class PreferenceArgumentImplementationTests(unittest.TestCase):
    def test_positional_arg(self):
        class T(C):
            def preference_cmp(self, a: Any, b: Any, pos_arg: int) -> int:
                if pos_arg == 1:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, 1)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, 0)
        self.assertTrue(max(elements) == e[0])

    def test_keyword_arg(self):
        class T(C):
            def preference_cmp(self, a: Any, b: Any, keyword_arg: int = 1) -> int:
                if keyword_arg == 1:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, keyword_arg=1)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, keyword_arg=0)
        self.assertTrue(max(elements) == e[0])

    def test_keyword_arg_default(self):
        class T(C):
            def preference_cmp(self, a: Any, b: Any, keyword_arg: int = 1) -> int:
                if keyword_arg == 1:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, keyword_arg=0)
        self.assertTrue(max(elements) == e[0])

    def test_positional_and_keyword_arg(self):
        class T(C):
            def preference_cmp(
                self, a: Any, b: Any, pos_arg: int, keyword_arg: int = 1
            ) -> int:
                if pos_arg == keyword_arg:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, 1, keyword_arg=0)
        self.assertTrue(max(elements) == e[0])
        e = a(elements, 1, keyword_arg=1)
        self.assertTrue(min(elements) == e[0])

    def test_arg_unpack(self):
        class T(C):
            def preference_cmp(self, a: Any, b: Any, *args) -> int:
                if args[0] == 1:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, 1)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, 0)
        self.assertTrue(max(elements) == e[0])

    def test_kwarg_unpack(self):
        class T(C):
            def preference_cmp(self, a: Any, b: Any, **kwargs) -> int:
                if kwargs["keyword_arg"] == 1:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, keyword_arg=1)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, keyword_arg=0)
        self.assertTrue(max(elements) == e[0])

    def test_arg_and_kwarg_unpack(self):
        class T(C):
            def preference_cmp(self, a: Any, b: Any, *args, **kwargs) -> int:
                if args[0] == kwargs["keyword_arg"]:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, 1, keyword_arg=1)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, 0, keyword_arg=1)
        self.assertTrue(max(elements) == e[0])

    def test_positional_keyword_arg_and_kwarg_unpack_arg(self):
        class T(C):
            def preference_cmp(
                self,
                a: Any,
                b: Any,
                pos_arg: int,
                *args,
                keyword_arg1: int = 1,
                **kwargs
            ) -> int:
                if pos_arg == keyword_arg1 == args[0] == kwargs["keyword_arg"]:
                    return -1 if a < b else 1 if a > b else 0
                else:
                    return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, 0, 0, keyword_arg1=0, keyword_arg=0)
        self.assertTrue(min(elements) == e[0])
        e = a(elements, 0, 1, keyword_arg1=1, keyword_arg=2)
        self.assertTrue(max(elements) == e[0])
        with self.assertRaises(IndexError):
            e = a(elements, 0, keyword_arg1=0)


class ArgsAndKwargsTests(unittest.TestCase):
    def test_action_pos_arg(self):
        class T(C):
            def action(self, chosen: Any, pos_arg: int) -> Any:
                return chosen + pos_arg

            def filter(self, chosen: Any) -> bool:
                return chosen % 2 == 0

            def preference_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

        a = T()
        e = a(elements, 2)
        expected_sum = sum(i + 2 for i in filter(lambda x: x % 2 == 0, elements))
        self.assertTrue(sum(e) == expected_sum)

    def test_action_and_filter_pos_arg(self):
        class T(C):
            def action(self, chosen: Any, pos_arg: int) -> Any:
                return chosen + pos_arg

            def filter(self, chosen: Any, filter_pos_arg: int) -> bool:
                return chosen % filter_pos_arg == 0

            def preference_cmp(self, a: Any, b: Any) -> int:
                return -1 if a < b else 1 if a > b else 0

        a = T()
        e = a(elements, 2)
        expected_sum = sum(i + 2 for i in filter(lambda x: x % 2 == 0, elements))
        self.assertTrue(sum(e) == expected_sum)

    def test_action_and_filter_and_preference_pos_arg(self):
        class T(C):
            def action(self, chosen: Any, pos_arg: int) -> Any:
                return chosen + pos_arg

            def filter(self, chosen: Any, filter_pos_arg: int) -> bool:
                return chosen % filter_pos_arg == 0

            def preference_cmp(self, a: Any, b: Any, pref_pos_arg: int) -> int:
                if pref_pos_arg == 2:
                    return -1 if a < b else 1 if a > b else 0
                return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements, 2)
        expected_result = list(i + 2 for i in filter(lambda x: x % 2 == 0, elements))
        expected_sum = sum(expected_result)
        self.assertTrue(sum(e) == expected_sum)
        self.assertTrue(min(expected_result) == e[0])

        # test the reverse sort
        e = a(elements, 1)
        expected_result = list(i + 1 for i in filter(lambda x: x % 1 == 0, elements))
        expected_sum = sum(expected_result)
        self.assertTrue(sum(e) == expected_sum)
        self.assertTrue(max(expected_result) == e[0])

    def test_action_and_filter_and_preference_keyword_arg(self):
        class T(C):
            def action(self, chosen: Any, action_arg: int = 1) -> Any:
                return chosen + action_arg

            def filter(self, chosen: Any, filter_arg: int = 1) -> bool:
                return chosen % filter_arg == 0

            def preference_cmp(self, a: Any, b: Any, pref_arg: int = 2) -> int:
                if pref_arg == 2:
                    return -1 if a < b else 1 if a > b else 0
                return 1 if a < b else -1 if a > b else 0

        a = T()
        e = a(elements)
        expected_result = list(i + 1 for i in filter(lambda x: x % 1 == 0, elements))
        expected_sum = sum(expected_result)
        self.assertTrue(sum(e) == expected_sum)
        self.assertTrue(min(expected_result) == e[0])

        # test the reverse sort
        e = a(elements, action_arg=3, filter_arg=2, pref_arg=2)
        expected_result = list(i + 3 for i in filter(lambda x: x % 2 == 0, elements))
        expected_sum = sum(expected_result)
        self.assertTrue(sum(e) == expected_sum)
        self.assertTrue(min(expected_result) == e[0])

    def test_overlapping_keyword_args(self):
        class T(C):
            def action(self, chosen: Any, kwarg1: int = 1) -> Any:
                return chosen + kwarg1

            def filter(self, chosen: Any, kwarg1: int = 1) -> bool:
                return chosen % kwarg1 == 0

        a = T()
        e = a(elements)
        expected_result = list(i + 1 for i in filter(lambda x: x % 1 == 0, elements))
        expected_sum = sum(expected_result)
        self.assertTrue(sum(e) == expected_sum)

    def test_overlapping_different_keyword_args(self):
        class CustomClass:
            def __init__(self, val: int) -> None:
                self.val = val

        with self.assertRaises(AttributeError):

            class T(C):
                def action(
                    self, chosen: Any, kwarg1: CustomClass = CustomClass(1)
                ) -> Any:
                    return chosen + kwarg1.val

                def filter(self, chosen: Any, kwarg1: int = 1) -> bool:
                    return chosen % kwarg1 == 0

    def test_overlapping_equivalent_keyword_args(self):
        class CustomClass:
            def __init__(self, val: int) -> None:
                self.val = val

        inst = CustomClass(1)

        class T(C):
            def action(self, chosen: Any, kwarg1: CustomClass = inst) -> Any:
                return chosen + kwarg1.val

            def filter(self, chosen: Any, kwarg1: CustomClass = inst) -> bool:
                return chosen % kwarg1 == 0

        self.assertTrue(True)  # pass if no error is thrown

    def test_mangled_keywords_by_reference_side_effects(self):
        class CustomClass:
            def __init__(self, val: int) -> None:
                self.val = val

        inst = CustomClass(1)

        class T(C):
            def action(self, chosen: Any, kwarg1: CustomClass = inst) -> Any:
                kwarg1.val = 2

        t_inst = T()
        t_inst([1])
        self.assertTrue(inst.val == 2)


if __name__ == "__main__":
    unittest.main()
