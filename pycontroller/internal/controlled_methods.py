import ast
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple

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
    def generate_expression(self) -> Tuple[ast.expr, List[ast.stmt]]:
        pass

    @abstractmethod
    def get_min_required_call_args(self) -> int:
        pass

    def get_new_lineno(self):
        self.current_setup_instructions_lineno += 1
        return self.current_setup_instructions_lineno


class Action(ControlledMethod):
    def generate_expression(self) -> Tuple[ast.expr, List[ast.stmt]]:
        # Create the nodes for the function name and the argument
        func_name = ast.Name(id=GENERATED_ACTION_FN_NAME, ctx=ast.Load())

        args = []
        args.append(ast.arg(arg=CHOSEN_NAME, annotation=None))
        args.extend(
            generate_positional_args(
                len(self.signature.non_class_positional_args)
                - self.get_min_required_call_args()
            )
        )
        if self.signature.has_arg_unpack:
            args.append(
                ast.Starred(
                    value=ast.Name(id=VAR_ARG_NAME, ctx=ast.Load()), ctx=ast.Load()
                )
            )

        kwargs = []
        for keyword, _ in self.signature.keyword_arguments:
            kwargs.append(
                ast.keyword(arg=keyword, value=ast.Name(id=keyword, ctx=ast.Load()))
            )
        if self.signature.has_kwarg_unpack:
            kwargs.append(
                ast.keyword(
                    arg=None,  # `arg` must be None for **kwargs
                    value=ast.Name(id=KWARG_NAME, ctx=ast.Load()),
                )
            )

        # Create the function call node
        call = ast.Call(func=func_name, args=args, keywords=kwargs)

        setup_statement = ast.Assign(
            targets=[ast.Name(id=GENERATED_ACTION_FN_NAME, ctx=ast.Store())],
            value=ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=ACTION_FN_NAME,
                ctx=ast.Load(),
            ),
            lineno=self.get_new_lineno(),
        )
        return call, [setup_statement]

    def get_min_required_call_args(self) -> int:
        return 1  # chosen


class Filter(ControlledMethod):
    def generate_expression(self) -> Tuple[ast.expr, List[ast.stmt]]:
        # Create the nodes for the function name and the arguments
        setup_statements = []
        filter_name = ast.Name(id="filter", ctx=ast.Load())

        args = []
        args.append(ast.arg(arg=CHOSEN_NAME, annotation=None))
        args.extend(
            generate_positional_args(
                len(self.signature.non_class_positional_args)
                - self.get_min_required_call_args()
            )
        )
        if self.signature.has_arg_unpack:
            args.append(
                ast.Starred(
                    value=ast.Name(id=VAR_ARG_NAME, ctx=ast.Load()), ctx=ast.Load()
                )
            )

        kwargs = []
        for keyword, _ in self.signature.keyword_arguments:
            kwargs.append(
                ast.keyword(arg=keyword, value=ast.Name(id=keyword, ctx=ast.Load()))
            )
        if self.signature.has_kwarg_unpack:
            kwargs.append(
                ast.keyword(
                    arg=None,  # `arg` must be None for **kwargs
                    value=ast.Name(id=KWARG_NAME, ctx=ast.Load()),
                )
            )

        elements_arg = ast.Name(id=PARTITION_NAME, ctx=ast.Load())
        if len(args) + len(kwargs) > self.get_min_required_call_args():
            # just do a generator expression (i for i in PARTITION if filter(i, *args, **kwargs))
            # Construct the generator expression
            filter_fn_name = ast.Name(id=GENERATED_FILTER_FN_NAME, ctx=ast.Load())

            call = ast.GeneratorExp(
                elt=ast.Name(id=CHOSEN_NAME, ctx=ast.Load()),
                generators=[
                    ast.comprehension(
                        target=ast.Name(id=CHOSEN_NAME, ctx=ast.Load()),
                        iter=elements_arg,
                        ifs=[ast.Call(func=filter_fn_name, args=args, keywords=kwargs)],
                        is_async=False,
                    )
                ],
            )

            # save a local instance of the preference function
            setup_statements.append(
                ast.Assign(
                    targets=[ast.Name(id=GENERATED_FILTER_FN_NAME, ctx=ast.Store())],
                    value=ast.Attribute(
                        value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                        attr=FILTER_FN_NAME,
                        ctx=ast.Load(),
                    ),
                    lineno=self.get_new_lineno(),
                )
            )
        else:
            filter_fn_name = ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()), attr=FILTER_FN_NAME
            )
            # Create the function call node
            call = ast.Call(
                func=filter_name, args=[filter_fn_name, elements_arg], keywords=[]
            )

        return call, setup_statements

    def get_min_required_call_args(self) -> int:
        return 1  # chosen


class Preference(ControlledMethod):
    def __init__(self, fn: Callable[..., Any], sort_reverse: bool) -> None:
        super().__init__(fn)
        self.sort_reverse = sort_reverse

    def generate_expression(
        self, get_elements_expression: ast.expr
    ) -> Tuple[ast.expr, List[ast.stmt]]:
        setup_statements = []

        # Create the nodes for the function names and the arguments
        if self.sort_reverse:
            sort_fn_name = ast.Name(id="_heapq_nlargest", ctx=ast.Load())
        else:
            sort_fn_name = ast.Name(id="_heapq_nsmallest", ctx=ast.Load())
        max_size = ast.Constant(value=sys.maxsize, kind=int)

        args = []
        args.append(ast.arg(arg=PREFERENCE_SELF_NAME, annotation=None))
        args.append(ast.arg(arg=PREFERENCE_OTHER_NAME, annotation=None))
        args.extend(
            generate_positional_args(
                len(self.signature.non_class_positional_args)
                - self.get_min_required_call_args()
            )
        )
        if self.signature.has_arg_unpack:
            args.append(
                ast.Starred(
                    value=ast.Name(id=VAR_ARG_NAME, ctx=ast.Load()), ctx=ast.Load()
                )
            )

        kwargs = []
        for keyword, _ in self.signature.keyword_arguments:
            kwargs.append(
                ast.keyword(arg=keyword, value=ast.Name(id=keyword, ctx=ast.Load()))
            )
        if self.signature.has_kwarg_unpack:
            kwargs.append(
                ast.keyword(
                    arg=None,  # `arg` must be None for **kwargs
                    value=ast.Name(id=KWARG_NAME, ctx=ast.Load()),
                )
            )

        if len(args) + len(kwargs) > self.get_min_required_call_args():
            preference_fn_name_original = ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=PREFERENCE_FN_NAME,
            )
            call = ast.Call(
                func=preference_fn_name_original, args=args, keywords=kwargs
            )
            # Lambda function: lambda x: _pref_fn(x, arg0, kwarg1=kwarg1)
            lambda_node = ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[
                        ast.arg(arg=PREFERENCE_SELF_NAME, annotation=None),
                        ast.arg(arg=PREFERENCE_OTHER_NAME, annotation=None),
                    ],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=call,
            )

            preference_fn_name = ast.Name(
                id=GENERATED_PREFERENCE_FN_NAME, ctx=ast.Store()
            )
            preference_fn = ast.Assign(
                targets=[preference_fn_name],
                value=lambda_node,
                lineno=self.get_new_lineno(),
            )
            setup_statements.append(preference_fn)

        else:
            preference_fn_name = ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=PREFERENCE_FN_NAME,
            )

        cmp_to_key_name = ast.Name(id="_cmp_to_key", ctx=ast.Load())
        key_arg = ast.keyword(
            arg="key",
            value=ast.Call(
                func=cmp_to_key_name, args=[preference_fn_name], keywords=[]
            ),
        )

        # Create the function call node
        call = ast.Call(
            func=sort_fn_name,
            args=[max_size, get_elements_expression],
            keywords=[key_arg],
        )

        return call, setup_statements

    def get_min_required_call_args(self) -> int:
        return 2  # a, b
