import ast
import dis
import functools
import inspect
import types
from functools import reduce
from heapq import nlargest, nsmallest
from textwrap import dedent
from typing import Callable


def contains_explicit_return(f):
    source = dedent(inspect.getsource(f))
    module = ast.parse(source)
    function_def = module.body[0]  # Get the function definition from the module
    return any(isinstance(node, ast.Return) for node in function_def.body)


class MetaDoController(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name == "DoController":
            return

        if "action" not in attrs:
            raise NotImplementedError(
                "Every controller needs to implement an 'action' method."
            )
        cls.__call__ = cls.action


class DoController(metaclass=MetaDoController):
    pass


class MetaDoAllController(type):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name == "DoAllController":
            return

        if "action" not in attrs:
            raise NotImplementedError(
                "Every controller needs to implement an 'action' method."
            )

        action_does_return = contains_explicit_return(cls.action)
        action_args = inspect.getfullargspec(cls.action).args
        args_with_elements = [action_args[0]] + ["elements"] + action_args[2:]

        call_signature = f"def _call_fn_({', '.join(args_with_elements)}):"

        fn_saves = f"__a = {args_with_elements[0]}.action"

        parse_cmd = ""
        if "filter" in attrs:
            fn_saves += f"\n\t__f = {args_with_elements[0]}.filter"
            parse_cmd += f"(__a({', '.join(['e'] + action_args[2:])}) for e in elements if __f({', '.join(['e'] + action_args[2:])}))"
        else:
            parse_cmd = f"(__a({', '.join(['e'] + action_args[2:])}) for e in elements)"

        if action_does_return:
            parse_cmd = "return " + parse_cmd
        else:
            parse_cmd = "list(" + parse_cmd + ")"

        fn = call_signature + "\n\t" + fn_saves + "\n\t" + parse_cmd

        ns = {}
        eval(
            compile(
                fn,
                "<string>",
                "exec",
            ),
            ns,
        )
        cls.__call__ = ns["_call_fn_"]


class DoAllController(metaclass=MetaDoAllController):
    pass
