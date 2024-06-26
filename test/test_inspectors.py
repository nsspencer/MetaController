import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import unittest

from metacontroller import Do
from metacontroller.internal.method_inspector import MethodInspector


class TestAssignments(unittest.TestCase):
    def test_controlled_method_assignments(self):

        def pre_controller_no_args(cls, arg1):
            cls.pre_controller_passed = arg1

        class BasicDo(Do):
            pre_controller_passed = False
            post_controller_passed = False
            pre_controller = pre_controller_no_args
            action = staticmethod(lambda: 1)
            post_controller = (
                lambda self, keyword_arg0=False: self.set_post_controller_value(
                    keyword_arg0
                )
            )

            def set_post_controller_value(self, value: bool):
                self.post_controller_passed = value

        inst = BasicDo()
        result = inst(True, keyword_arg0=True)
        self.assertTrue(inst.pre_controller_passed)
        self.assertTrue(result == 1)
        self.assertTrue(inst.post_controller_passed)


class DummyContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def dummy_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class TestMethodReturns(unittest.TestCase):

    def test_value_return(self):
        def return_explicit_value():
            return 42

        fn = MethodInspector(return_explicit_value)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_conditional_value_return(self):
        def return_in_conditional(x):
            if x > 0:
                return x
            else:
                return -x

        fn = MethodInspector(return_in_conditional)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_loop_value_return(self):
        def return_in_loop(lst):
            for item in lst:
                if item > 0:
                    return item
            return

        fn = MethodInspector(return_in_loop)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertTrue(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_try_except_value_return(self):
        def return_in_try_except(x):
            try:
                return 1 / x
            except ZeroDivisionError:
                return float("inf")

        fn = MethodInspector(return_in_try_except)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_nested_function_value_return(self):
        def outer_function():
            def inner_function():
                return "inner"

            return inner_function()

        fn = MethodInspector(outer_function)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_lambda_function_value_return(self):
        def return_from_lambda():
            f = lambda x: x + 1
            return f(5)

        fn = MethodInspector(return_from_lambda)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_no_return(self):
        def no_return():
            pass

        fn = MethodInspector(no_return)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_return_none(self):
        def return_none():
            return

        fn = MethodInspector(return_none)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertTrue(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_no_return_in_conditional(self):
        def no_return_in_conditional(x):
            if x > 0:
                x += 1
            else:
                x -= 1

        fn = MethodInspector(no_return_in_conditional)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_no_return_in_loop(self):
        def no_return_in_loop(lst):
            for item in lst:
                item += 1

        fn = MethodInspector(no_return_in_loop)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_no_return_in_try_except(self):
        def no_return_in_try_except(x):
            try:
                x += 1
            except:
                x -= 1

        fn = MethodInspector(no_return_in_try_except)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_no_return_nested_function(self):
        def no_return_outer():
            def no_return_inner():
                pass

            no_return_inner()

        fn = MethodInspector(no_return_outer)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_no_return_nested_function_with_inner_return(self):
        def no_return_outer():
            def no_return_inner():
                return True

            no_return_inner()

        fn = MethodInspector(no_return_outer)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_mixed_return(self):
        def mixed_return(x):
            if x > 0:
                return x
            x -= 1

        fn = MethodInspector(mixed_return)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_return_in_loop_no_after(self):
        def return_in_loop_no_after(lst):
            for item in lst:
                if item > 0:
                    return item
            print("No positive numbers")

        fn = MethodInspector(return_in_loop_no_after)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_mixed_try_except(self):
        def mixed_try_except(x):
            try:
                return 1 / x
            except ZeroDivisionError:
                x -= 1

        fn = MethodInspector(mixed_try_except)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_yield_value(self):
        def generator_function():
            yield 42

        fn = MethodInspector(generator_function)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertTrue(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_yield_in_loop(self):
        def generator_in_loop(lst):
            for item in lst:
                yield item

        fn = MethodInspector(generator_in_loop)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertTrue(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_yield_in_conditional(self):
        def generator_in_conditional(x):
            if x > 0:
                yield x
            else:
                yield -x

        fn = MethodInspector(generator_in_conditional)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertTrue(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_yield_from_value(self):
        def generator_yield_from():
            yield from [1, 2, 3]

        fn = MethodInspector(generator_yield_from)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertTrue(fn.has_value_yield_from)

    def test_yield_from_in_loop(self):
        def generator_yield_from_loop(lst):
            for sublist in lst:
                yield from sublist

        fn = MethodInspector(generator_yield_from_loop)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertTrue(fn.has_value_yield_from)

    def test_yield_and_return(self):
        def generator_with_return(x):
            yield x
            return x

        fn = MethodInspector(generator_with_return)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertTrue(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)


class TestFunctionsWithClasses(unittest.TestCase):

    def test_function_with_inner_class_return(self):
        def function_with_class():
            class InnerClass:
                def method(self):
                    return 42

            return "outer"

        fn = MethodInspector(function_with_class)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_function_with_inner_class_no_return(self):
        def function_with_class():
            class InnerClass:
                def method(self):
                    return 42

            pass

        fn = MethodInspector(function_with_class)
        self.assertFalse(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_function_with_inner_class_and_with_block(self):
        def function_with_class_and_with():
            class InnerClass:
                def method(self):
                    return 42

            with DummyContextManager():
                pass
            return "outer"

        fn = MethodInspector(function_with_class_and_with)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_function_with_inner_class_and_closure(self):
        def function_with_class_and_closure():
            class InnerClass:
                def method(self):
                    return 42

            def inner_function():
                return "inner"

            return inner_function()

        fn = MethodInspector(function_with_class_and_closure)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_function_with_inner_class_and_lambda(self):
        def function_with_class_and_lambda():
            class InnerClass:
                def method(self):
                    return 42

            f = lambda x: x + 1
            return f(5)

        fn = MethodInspector(function_with_class_and_lambda)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_function_with_inner_class_yield(self):
        def function_with_class_and_yield():
            class InnerClass:
                def method(self):
                    yield 42

            return "outer"

        fn = MethodInspector(function_with_class_and_yield)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)

    def test_function_with_inner_class_yield_from(self):
        def function_with_class_and_yield_from():
            class InnerClass:
                def method(self):
                    yield from [1, 2, 3]

            return "outer"

        fn = MethodInspector(function_with_class_and_yield_from)
        self.assertTrue(fn.has_explicit_value_return)
        self.assertFalse(fn.has_explicit_void_return)
        self.assertFalse(fn.has_value_yield)
        self.assertFalse(fn.has_value_yield_from)


class TestMethodInspectorAdditionalProperties(unittest.TestCase):

    def test_decorated_function(self):
        @dummy_decorator
        def decorated_function():
            return 42

        fn = MethodInspector(decorated_function)
        self.assertFalse(fn.is_staticmethod)
        self.assertFalse(fn.is_lambda)

    def test_lambda_function(self):
        lambda_function = lambda x: x + 1

        fn = MethodInspector(lambda_function)
        self.assertFalse(fn.is_staticmethod)
        self.assertTrue(fn.is_lambda)

    def test_decorated_lambda_function(self):
        decorated_lambda = dummy_decorator(lambda x: x + 1)

        fn = MethodInspector(decorated_lambda)
        self.assertFalse(fn.is_staticmethod)
        self.assertFalse(fn.is_lambda)

    def test_function_with_inner_class_and_decorator(self):
        def function_with_class_and_decorator():
            @dummy_decorator
            class InnerClass:
                def method(self):
                    return 42

            return "outer"

        fn = MethodInspector(function_with_class_and_decorator)
        self.assertFalse(fn.is_staticmethod)
        self.assertFalse(fn.is_lambda)


class ArgClass:
    # Example functions for testing
    def simple_function(self, a, /, b=10, *args, c, d=20, **kwargs):
        pass

    def function_with_annotations(self, x: int, y: str = "default") -> float:
        pass


class TestMethodInspectorProperties(unittest.TestCase):

    def setUp(self):
        # Setup MethodInspector instances for each function
        inst = ArgClass()
        self.simple_fn = MethodInspector(inst.simple_function)
        self.annotation_fn = MethodInspector(inst.function_with_annotations)

    def test_posonlyargs(self):
        self.assertEqual(self.simple_fn.posonlyargs, ["a"])

    def test_args(self):
        self.assertEqual(self.simple_fn.args, ["self", "a", "b"])

    def test_call_args(self):
        self.assertEqual(self.simple_fn.call_args, ["a", "b"])

    def test_num_parameters(self):
        self.assertEqual(self.simple_fn.num_parameters, 7)

    def test_num_call_parameters(self):
        self.assertEqual(self.simple_fn.num_call_parameters, 6)

    def test_varargs(self):
        self.assertEqual(self.simple_fn.varargs, "args")

    def test_varkw(self):
        self.assertEqual(self.simple_fn.varkw, "kwargs")

    def test_defaults(self):
        self.assertEqual(self.simple_fn.defaults, (10,))

    def test_kwonlyargs(self):
        self.assertEqual(self.simple_fn.kwonlyargs, ["c", "d"])

    def test_kwonlydefaults(self):
        self.assertEqual(self.simple_fn.kwonlydefaults, {"d": 20})

    def test_annotations(self):
        self.assertEqual(
            self.annotation_fn.annotations, {"x": int, "y": str, "return": float}
        )

    def test_has_arg_unpack(self):
        self.assertTrue(self.simple_fn.has_arg_unpack)

    def test_has_kwarg_unpack(self):
        self.assertTrue(self.simple_fn.has_kwarg_unpack)


if __name__ == "__main__":
    unittest.main()
