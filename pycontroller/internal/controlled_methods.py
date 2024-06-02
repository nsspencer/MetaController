import ast
import inspect
import textwrap
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple, Union

from pycontroller.internal.namespace import *
from pycontroller.internal.namespace import MANGLED_KWARG_NAME
from pycontroller.internal.signature_helper import SignatureHelper
from pycontroller.internal.utils import generate_positional_args


class ControlledMethod(ABC):
    __slots__ = "fn", "signature"
    current_setup_instructions_lineno = 0

    def __init__(self, fn: Callable, optimize: bool = False) -> None:
        self.fn = fn
        self.signature = SignatureHelper(self.fn)
        self.optimize = optimize

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
    ) -> Tuple[ast.Call, Union[ast.FunctionDef | None]]:

        # get the required arguments that will be passed to this function
        required_pos_args = [
            ast.arg(arg=arg, annotation=None)
            for arg in self.signature.full_call_arg_spec.args[
                : self.get_min_required_call_args()
            ]
        ]
        inner_args = ast.arguments(
            posonlyargs=[],
            args=required_pos_args,
            vararg=[],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=[],
            defaults=[],
        )

        _extra_call_args = self.signature.full_call_arg_spec.args[
            self.get_min_required_call_args() :
        ]
        _extra_call_args = _extra_call_args[
            : len(_extra_call_args) - len(self.signature.defaults)
        ]

        if self.optimize == False:
            # call the users method and pass in all the required arguments
            _inner_call_args = required_pos_args[:]

            # add the position only/non-defaulted arguments
            _inner_call_args.extend(generate_positional_args(len(_extra_call_args)))

            # add the defaulted arguments
            _inner_call_args.extend(
                [
                    ast.arg(arg=keyword, annotation=None)
                    for keyword, _ in self.signature.get_defaulted_args()
                ]
            )

            # add arg unpack
            if self.signature.has_arg_unpack:
                _inner_call_args.append(
                    ast.Starred(
                        value=ast.Name(id=VAR_ARG_NAME, ctx=ast.Load()), ctx=ast.Load()
                    )
                )

            # generate the keywords
            _inner_call_keywords = []

            # add keyword only arguments
            _inner_call_keywords.extend(
                [
                    ast.keyword(arg=keyword, value=ast.Name(id=keyword, ctx=ast.Load()))
                    for keyword, _ in self.signature.get_keyword_only_args()
                ]
            )

            # add kwarg unpack
            if self.signature.has_kwarg_unpack:
                _inner_call_keywords.append(
                    ast.keyword(arg=None, value=ast.Name(id=KWARG_NAME, ctx=ast.Load()))
                )

            method_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=self.fn.__name__,
                ),
                args=_inner_call_args,
                keywords=_inner_call_keywords,
            )

            lambda_expr = ast.Lambda(args=inner_args, body=method_call)
            return lambda_expr, None

        ######################
        # OPTIMIZATIONS ARE ON
        #

        # get the arguments needed for the outer wrapper
        args = [ast.arg(arg=arg, annotation=None) for arg in _extra_call_args]

        vararg = (
            ast.arg(arg=self.signature.varargs, annotation=None)
            if self.signature.has_arg_unpack
            else None
        )
        kwarg = (
            ast.arg(arg=self.signature.varkw, annotation=None)
            if self.signature.has_kwarg_unpack
            else None
        )

        # Create the outer_args with the correct structure
        outer_args = ast.arguments(
            posonlyargs=[],
            args=args,
            vararg=vararg,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=kwarg,
            defaults=[],
        )

        # parse the source code from the method and inline it in the wrapper to avoid
        # the stack frame overhead.
        method_body = (
            ast.parse(textwrap.dedent(inspect.getsource(self.fn))).body[0].body
        )
        inner_wrapper = ast.FunctionDef(
            name="inner_fn",
            args=inner_args,
            body=method_body,
            decorator_list=[],
            returns=None,
            lineno=0,
        )
        return_val = ast.Return(value=ast.Name(id="inner_fn", ctx=ast.Load()))
        wrapped_body = [inner_wrapper, return_val]

        wrapper_fn = ast.FunctionDef(
            name=wrapper_name,
            args=outer_args,
            body=wrapped_body,
            decorator_list=[],
            returns=None,
            lineno=self.get_new_lineno(),
        )

        call_args = []
        call_args.extend(generate_positional_args(len(args)))
        if self.signature.has_arg_unpack:
            call_args.append(
                ast.Starred(
                    value=ast.Name(id=VAR_ARG_NAME, ctx=ast.Load()), ctx=ast.Load()
                )
            )

        call_keywords = []
        if self.signature.has_kwarg_unpack:
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

        # determine if we need to wrap this function call because it needs additional arguments
        full_arg_spec = self.signature.full_call_arg_spec
        if (
            len(full_arg_spec.args) - self.get_min_required_call_args() > 0
            or len(self.signature.kwonlyargs) != 0
            or self.signature.has_arg_unpack
            or self.signature.has_kwarg_unpack
        ):
            call_fn, wrapper = self.generate_wrapped_function("wrapped_action")
            if wrapper:
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

        # determine if we need to wrap this function call because it needs additional arguments
        full_arg_spec = self.signature.full_call_arg_spec
        if (
            len(full_arg_spec.args) - self.get_min_required_call_args() > 0
            or len(self.signature.kwonlyargs) != 0
            or self.signature.has_arg_unpack
            or self.signature.has_kwarg_unpack
        ):
            call_fn, wrapper = self.generate_wrapped_function("wrapped_filter")
            if wrapper:
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
        self,
        fn: Callable[..., Any],
        simple_sort: bool,
        reverse_sort: bool,
        is_comparator: bool = False,
        optimize: bool = False,
    ) -> None:
        super().__init__(fn, optimize)
        self.reverse_sort = reverse_sort
        self.simple_sort = simple_sort
        self.is_comparator = is_comparator

    def generate_expression(
        self,
        get_elements_expr: ast.expr,
        max_chosen: Union[ast.Name | ast.Constant | None] = None,
    ) -> Tuple[ast.expr, List[ast.stmt]]:
        setup_statements = []

        # determine if we need to wrap this function call because it needs additional arguments
        full_arg_spec = self.signature.full_call_arg_spec
        if (
            len(full_arg_spec.args) - self.get_min_required_call_args() > 0
            or len(self.signature.kwonlyargs) != 0
            or self.signature.has_arg_unpack
            or self.signature.has_kwarg_unpack
        ):
            wrapper_call_fn, wrapper = self.generate_wrapped_function(
                "wrapped_preference"
            )
            if wrapper:
                setup_statements.append(wrapper)

        else:
            if self.is_comparator:
                wrapper_call_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=SORT_CMP_FN_NAME,
                )
            else:
                wrapper_call_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=SORT_KEY_FN_NAME,
                )

        # define the args for the sort method
        sort_args = []
        sort_kwargs = []

        # Create the nodes for the function names and the arguments
        if max_chosen is not None:
            if self.reverse_sort:
                sort_fn_name = ast.Name(id="_heapq_nlargest", ctx=ast.Load())
            else:
                sort_fn_name = ast.Name(id="_heapq_nsmallest", ctx=ast.Load())
            sort_args += [max_chosen, get_elements_expr]

        else:
            sort_fn_name = ast.Name(id="sorted", ctx=ast.Load())
            sort_args += [get_elements_expr]
            if self.reverse_sort:
                sort_kwargs.append(
                    ast.keyword(
                        arg="reverse", value=ast.Constant(value=True, kind=bool)
                    )
                )

        if not self.simple_sort:
            if self.is_comparator:
                cmp_to_key_name = ast.Name(id="_cmp_to_key", ctx=ast.Load())
                sort_kwargs.append(
                    ast.keyword(
                        arg="key",
                        value=ast.Call(
                            func=cmp_to_key_name, args=[wrapper_call_fn], keywords=[]
                        ),
                    )
                )
            else:
                sort_kwargs.append(ast.keyword(arg="key", value=wrapper_call_fn))

        call_fn = ast.Call(func=sort_fn_name, args=sort_args, keywords=sort_kwargs)

        return call_fn, setup_statements

    def get_min_required_call_args(self) -> int:
        if self.is_comparator:
            return 2  # a, b
        else:
            return 1  # chosen
