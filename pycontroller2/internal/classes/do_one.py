import ast
import warnings
from functools import cmp_to_key
from heapq import nlargest, nsmallest
from itertools import islice
from typing import Any, Callable

from pycontroller2.internal.controlled_method import MethodInvocation
from pycontroller2.internal.exceptions import InvalidControllerMethod
from pycontroller2.internal.namespace import (
    ACTION_RESULT_ASSIGNMENT_NAME,
    CHOSEN_ARG_NAME,
    FOLD_METHOD_NAME,
    GENERATED_CALL_METHOD_NAME,
    PARTITION_ARG_NAME,
    PREFERENCE_CMP_METHOD_NAME,
    PREFERENCE_KEY_METHOD_NAME,
)

from ._base import BaseControllerImplementation


class DoOneImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(cls, name, bases, attrs, stack_frame)

    def validate(self) -> None:
        super().validate()
        if self.has_preference_key and self.has_preference_cmp:
            err = f'DoOne controller "{self.name}" is invalid because both preference methods ("{PREFERENCE_KEY_METHOD_NAME}", and "{PREFERENCE_CMP_METHOD_NAME}") are defined.'
            err += f' You must define only one. Note that "{PREFERENCE_KEY_METHOD_NAME}" is more optimal.'
            raise InvalidControllerMethod(err)

        if self.has_fold:
            warnings.warn(
                f'DoOne does not support the "{FOLD_METHOD_NAME}" method, but one is defined in "{self.name}". It will be ignored.'
            )

    def generate_call_method(self) -> Callable[..., Any]:
        body = []
        additional_globals = {}
        get_elements = ast.Name(id=PARTITION_ARG_NAME, ctx=ast.Load())

        if self.has_pre_controller:
            pre_controller_call = MethodInvocation(
                self.pre_controller
            ).to_function_call()
            body.append(ast.Expr(value=pre_controller_call))

        if self.has_filter:
            filter_lambda = MethodInvocation(self.filter).to_lambda(
                [self.filter.call_args[0]]
            )
            get_elements = ast.Call(
                func=ast.Name(id="filter", ctx=ast.Load()),
                args=[filter_lambda, get_elements],
                keywords=[],
            )

        if self.has_preference_key:
            preference_lambda = MethodInvocation(self.preference_key).to_lambda(
                [self.preference_key.call_args[0]]
            )

            if self.cls.reverse_preference:
                sort_fn = ast.Name(id="nlargest", ctx=ast.Load())
                additional_globals["nlargest"] = nlargest
            else:
                sort_fn = ast.Name(id="nsmallest", ctx=ast.Load())
                additional_globals["nsmallest"] = nsmallest

            get_elements = ast.Call(
                func=sort_fn,
                args=[ast.Constant(value=1, kind="int"), get_elements],
                keywords=[ast.keyword(arg="key", value=preference_lambda)],
            )

        if self.has_preference_cmp:
            preference_lambda = MethodInvocation(self.preference_cmp).to_lambda(
                [self.preference_cmp.call_args[:2]]
            )

            if self.cls.reverse_preference:
                sort_fn = ast.Name(id="nlargest", ctx=ast.Load())
                additional_globals["nlargest"] = nlargest
            else:
                sort_fn = ast.Name(id="nsmallest", ctx=ast.Load())
                additional_globals["nsmallest"] = nsmallest

            get_elements = ast.Call(
                func=sort_fn,
                args=[ast.Constant(value=1, kind="int"), get_elements],
                keywords=[
                    ast.keyword(
                        arg="key",
                        value=ast.Call(
                            func=ast.Name(id="cmp_to_key", ctx=ast.Load()),
                            args=[preference_lambda],
                            keywords=[],
                        ),
                    )
                ],
            )
            additional_globals["cmp_to_key"] = cmp_to_key

        if not self.has_preference_key and not self.has_preference_cmp:
            get_elements = ast.Call(
                func=ast.Name(id="islice", ctx=ast.Load()),
                args=[get_elements, 1],
                keywords=[],
            )
            additional_globals["islice"] = islice

            get_elements = ast.Call(
                func=ast.Name(id="list", ctx=ast.Load()),
                args=[get_elements],
                keywords=[],
            )

        # get the chosen element
        chosen_element = ast.Assign(
            targets=[ast.Name(id=CHOSEN_ARG_NAME, ctx=ast.Store())], value=get_elements
        )
        result = ast.Assign(
            targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
            value=ast.Constant(value=None, kind=None),
        )
        body.append(result)
        body.append(chosen_element)

        if self.has_action:
            action_result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=MethodInvocation(self.action).to_function_call(),
            )

            # check if there is an element that we should act on
            if_check = ast.If(
                test=ast.Compare(
                    left=ast.Call(
                        func=ast.Name(id="len", ctx=ast.Load()),
                        args=[ast.Name(id=CHOSEN_ARG_NAME, ctx=ast.Load())],
                        keywords=[],
                    ),
                    ops=[ast.NotEq()],
                    comparators=[ast.Constant(value=0, kind="int")],
                ),
                body=[
                    ast.Assign(
                        targets=[
                            ast.Name(id=self.action.call_args[0], ctx=ast.Store())
                        ],
                        value=ast.Subscript(
                            value=ast.Name(id=CHOSEN_ARG_NAME, ctx=ast.Load()),
                            slice=ast.Num(n=0),
                            ctx=ast.Load(),
                        ),
                    ),
                    action_result,
                ],
                orelse=[],
            )
            body.append(if_check)

        if self.has_post_controller:
            post_controller_call = MethodInvocation(
                self.post_controller
            ).to_function_call()
            body.append(ast.Expr(value=post_controller_call))

        body.append(
            ast.Return(value=ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load()))
        )

        args, saved_defaults = self.get_call_args(
            use_class_arg=True,
            use_k_arg=False,
            use_partition_arg=True,
            required_action_args=1,
        )
        additional_globals.update(saved_defaults)
        call_fn = ast.FunctionDef(
            name=GENERATED_CALL_METHOD_NAME,
            args=args,
            body=body,
            decorator_list=[],
            type_params=[],
        )

        module = ast.fix_missing_locations(ast.Module(body=[call_fn], type_ignores=[]))
        return self.compile_call_method(module, additional_globals)
