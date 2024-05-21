import ast
import inspect
import sys
import textwrap
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple, Union

from pycontroller.internal.namespace import *
from pycontroller.internal.signature_helper import SignatureHelper
from pycontroller.internal.utils import generate_positional_args


class ControlledMethod(ABC):
    __slots__ = "fn", "signature"
    current_setup_instructions_lineno = 0

    def __init__(self, fn: Callable) -> None:
        self.fn = fn
        self.signature = SignatureHelper(self.fn)

    @abstractmethod
    def generate_expression(
        self,
        get_elements_expr: ast.expr,
        max_chosen: Union[ast.Name | ast.Constant | None] = None,
    ) -> Tuple[ast.expr, List[ast.stmt]]:
        pass

    @abstractmethod
    def get_min_required_call_args(self) -> int:
        pass

    def get_new_lineno(self):
        self.current_setup_instructions_lineno += 1
        return self.current_setup_instructions_lineno

    def generate_wrapped_function(
        self, wrapper_name: str
    ) -> Tuple[ast.Call, ast.FunctionDef]:
        fn_body = ast.parse(textwrap.dedent(inspect.getsource(self.fn))).body[0].body

        required_pos_args = self.signature.full_call_arg_spec.args[
            : self.get_min_required_call_args()
        ]
        inner_args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=arg, annotation=None) for arg in required_pos_args],
            vararg=[],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=[],
            defaults=[],
        )
        inner_wrapper = ast.FunctionDef(
            name="inner_fn",
            args=inner_args,
            body=fn_body,
            decorator_list=[],
            returns=None,
            lineno=0,
        )

        return_val = ast.Return(value=ast.Name(id="inner_fn", ctx=ast.Load()))
        args = self.fullargspec_to_arguments(self.signature.full_call_arg_spec)
        args.args = args.args[
            self.get_min_required_call_args() : -len(args.defaults) or None
        ]
        args.defaults = []
        wrapper_fn = ast.FunctionDef(
            name=wrapper_name,
            args=args,
            body=[inner_wrapper, return_val],
            decorator_list=[],
            returns=None,
            lineno=self.get_new_lineno(),
        )

        call_args = generate_positional_args(len(args.args))
        call_keywords = []
        if args.vararg:
            call_args.append(
                ast.Starred(
                    value=ast.Name(id=VAR_ARG_NAME, ctx=ast.Load()), ctx=ast.Load()
                )
            )
        if args.kwarg:
            call_keywords.append(
                ast.keyword(arg=None, value=ast.Name(id=KWARG_NAME, ctx=ast.Load()))
            )

        # generate the call fn
        call_fn = ast.Call(
            func=ast.Name(wrapper_name, ctx=ast.Load()),
            args=call_args,
            keywords=call_keywords,
        )

        return call_fn, wrapper_fn

    @staticmethod
    def fullargspec_to_arguments(fullargspec):
        args = [ast.arg(arg=arg) for arg in fullargspec.args]

        defaults = []
        if fullargspec.defaults is not None:
            for default in fullargspec.defaults:
                defaults.append(ast.Constant(value=default))

        kwonlyargs = [
            ast.arg(arg=arg, annotation=None) for arg in fullargspec.kwonlyargs
        ]

        kwdefaults = []
        if fullargspec.kwonlydefaults is not None:
            kwdefaults = [
                ast.Constant(value=default) if default is not None else None
                for arg, default in zip(
                    fullargspec.kwonlyargs, fullargspec.kwonlydefaults.values()
                )
            ]

        vararg = (
            ast.arg(
                arg=fullargspec.varargs,
                annotation=None,
            )
            if fullargspec.varargs
            else None
        )
        kwarg = (
            ast.arg(
                arg=fullargspec.varkw,
                annotation=None,
            )
            if fullargspec.varkw
            else None
        )

        return ast.arguments(
            posonlyargs=[],
            args=args,
            defaults=defaults,
            kwonlyargs=kwonlyargs,
            kw_defaults=kwdefaults,
            vararg=vararg,
            kwarg=kwarg,
        )


class Action(ControlledMethod):
    def generate_expression(
        self,
        get_elements_expr: ast.expr,
        max_chosen: Union[ast.Name | ast.Constant | None] = None,
    ) -> Tuple[ast.expr, List[ast.stmt]]:
        setup_statements = []

        if (
            len(self.signature.full_call_arg_spec.args)
            - self.get_min_required_call_args()
            > 0
            or self.signature.has_arg_unpack
            or self.signature.has_kwarg_unpack
        ):
            call_fn, wrapper = self.generate_wrapped_function("wrapped_action")
            setup_statements.append(wrapper)
        else:
            call_fn = ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=ACTION_FN_NAME,
            )

        if max_chosen:
            get_elements_expr = ast.Call(
                func=ast.Name(id="_itertools_islice", ctx=ast.Load()),
                args=[get_elements_expr, max_chosen],
                keywords=[],
            )

        call = ast.Call(
            func=ast.Name(id="map", ctx=ast.Load()),
            args=[call_fn, get_elements_expr],
            keywords=[],
        )

        # list_call = ast.Call(
        #     func=ast.Name(id="list", ctx=ast.Load()), args=[call], keywords=[]
        # )

        return call, setup_statements

    def get_min_required_call_args(self) -> int:
        return 1  # chosen


class Filter(ControlledMethod):
    def generate_expression(
        self,
        get_elements_expr: ast.expr,
        max_chosen: Union[ast.Name | ast.Constant | None] = None,
    ) -> Tuple[ast.expr, List[ast.stmt]]:
        setup_statements = []

        if (
            len(self.signature.full_call_arg_spec.args)
            - self.get_min_required_call_args()
            > 0
            or self.signature.has_arg_unpack
            or self.signature.has_kwarg_unpack
        ):
            call_fn, wrapper = self.generate_wrapped_function("wrapped_filter")
            setup_statements.append(wrapper)
        else:
            call_fn = ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=FILTER_FN_NAME,
            )

        if max_chosen:
            get_elements_expr = ast.Call(
                func=ast.Name(id="_itertools_islice", ctx=ast.Load()),
                args=[get_elements_expr, max_chosen],
                keywords=[],
            )

        call = ast.Call(
            func=ast.Name(id="filter", ctx=ast.Load()),
            args=[call_fn, get_elements_expr],
            keywords=[],
        )

        return call, setup_statements

    def get_min_required_call_args(self) -> int:
        return 1  # chosen


class Preference(ControlledMethod):
    def __init__(
        self, fn: Callable[..., Any], sort_with_key: bool, sort_reverse: bool
    ) -> None:
        super().__init__(fn)
        self.sort_reverse = sort_reverse
        self.sort_with_key = sort_with_key

    def generate_expression(
        self,
        get_elements_expr: ast.expr,
        max_chosen: Union[ast.Name | ast.Constant | None] = None,
    ) -> Tuple[ast.expr, List[ast.stmt]]:
        setup_statements = []

        if (
            len(self.signature.full_call_arg_spec.args)
            - self.get_min_required_call_args()
            > 0
            or self.signature.has_arg_unpack
            or self.signature.has_kwarg_unpack
        ):
            wrapper_call_fn, wrapper = self.generate_wrapped_function(
                "wrapped_preference"
            )
            setup_statements.append(wrapper)
        else:
            wrapper_call_fn = ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=PREFERENCE_FN_NAME,
            )

        # define the args for the sort method
        sort_args = []
        sort_kwargs = []

        # Create the nodes for the function names and the arguments
        if max_chosen is not None:
            if self.sort_reverse:
                sort_fn_name = ast.Name(id="_heapq_nlargest", ctx=ast.Load())
            else:
                sort_fn_name = ast.Name(id="_heapq_nsmallest", ctx=ast.Load())
            sort_args += [max_chosen, get_elements_expr]

        else:
            sort_fn_name = ast.Name(id="sorted", ctx=ast.Load())
            sort_args += [get_elements_expr]
            if self.sort_reverse:
                sort_kwargs.append(
                    ast.keyword(
                        arg="reverse", value=ast.Constant(value=True, kind=bool)
                    )
                )

        if not self.sort_with_key:
            cmp_to_key_name = ast.Name(id="_cmp_to_key", ctx=ast.Load())
            sort_kwargs.append(
                ast.keyword(
                    arg="key",
                    value=ast.Call(
                        func=cmp_to_key_name, args=[wrapper_call_fn], keywords=[]
                    ),
                )
            )

        call_fn = ast.Call(func=sort_fn_name, args=sort_args, keywords=sort_kwargs)

        return call_fn, setup_statements

    def get_min_required_call_args(self) -> int:
        return 2  # a, b
