import ast
import warnings
from functools import cmp_to_key
from heapq import nlargest, nsmallest
from itertools import islice
from typing import Any, Callable

from pycontroller2.internal.controlled_method import MethodInvocation
from pycontroller2.internal.exceptions import InvalidControllerMethod
from pycontroller2.internal.namespace import (
    ACTION_METHOD_NAME,
    ACTION_RESULT_ASSIGNMENT_NAME,
    CHOSEN_ARG_NAME,
    CLASS_ARG_NAME,
    FILTER_METHOD_NAME,
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
            err = f'DoOne controller "{self.name}" is invalid because both preference methods ("{PREFERENCE_KEY_METHOD_NAME}" and "{PREFERENCE_CMP_METHOD_NAME}") are defined.'
            err += f' You must define only one. Note that "{PREFERENCE_KEY_METHOD_NAME}" is more performant.'
            raise InvalidControllerMethod(err)

        if self.has_fold:
            warnings.warn(
                f'DoOne does not support the "{FOLD_METHOD_NAME}" method, but one is defined in "{self.name}". It will be ignored.'
            )

        if self.has_filter:
            if len(self.filter.call_args) < 1:
                raise AttributeError(
                    f'"{FILTER_METHOD_NAME}" should be defined with at least 1 non-class argument (chosen), but 0 were given.'
                )

        if self.has_preference_key:
            if len(self.preference_key.call_args) < 1:
                raise AttributeError(
                    f'"{PREFERENCE_KEY_METHOD_NAME}" should be defined with at least 1 non-class argument (chosen), but 0 were given.'
                )

        if self.has_preference_cmp:
            if len(self.preference_cmp.call_args) < 2:
                raise AttributeError(
                    f'"{PREFERENCE_CMP_METHOD_NAME}" should be defined with at least 2 non-class arguments (a, b), but {len(self.preference_cmp.call_args)} were given.'
                )

        if self.has_action:
            if len(self.action.call_args) < 1:
                raise AttributeError(
                    f'"{ACTION_METHOD_NAME}" should be defined with at least 1 non-class argument (chosen), but 0 were given.'
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
            if self.filter.num_call_parameters != 1:
                filter_fn = MethodInvocation(self.filter).to_lambda(
                    [self.filter.call_args[0]]
                )
            else:
                filter_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=FILTER_METHOD_NAME,
                    ctx=ast.Load(),
                )
            get_elements = ast.Call(
                func=ast.Name(id="filter", ctx=ast.Load()),
                args=[filter_fn, get_elements],
                keywords=[],
            )

        if self.has_preference_key:
            if self.preference_key.num_call_parameters != 1:
                preference_fn = MethodInvocation(self.preference_key).to_lambda(
                    [self.preference_key.call_args[0]]
                )
            else:
                preference_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=PREFERENCE_KEY_METHOD_NAME,
                    ctx=ast.Load(),
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
                keywords=[ast.keyword(arg="key", value=preference_fn)],
            )

        if self.has_preference_cmp:
            if self.preference_cmp.num_call_parameters != 2:
                preference_fn = MethodInvocation(self.preference_cmp).to_lambda(
                    self.preference_cmp.call_args[:2]
                )
            else:
                preference_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=PREFERENCE_CMP_METHOD_NAME,
                    ctx=ast.Load(),
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
                            args=[preference_fn],
                            keywords=[],
                        ),
                    )
                ],
            )
            additional_globals["cmp_to_key"] = cmp_to_key

        if not self.has_preference_key and not self.has_preference_cmp:
            get_elements = ast.Call(
                func=ast.Name(id="islice", ctx=ast.Load()),
                args=[get_elements, ast.Constant(value=1, kind="int")],
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
        body.append(chosen_element)

        if self.has_action:
            action_invoke = MethodInvocation(self.action)
            action_args, action_keywords = action_invoke.get_call_args_and_keywords()

            # remove the original argument and replace it with the index 0 of the get_elements statement
            action_args.pop(0)
            action_args.insert(
                0,
                ast.Subscript(
                    value=ast.Name(id=CHOSEN_ARG_NAME, ctx=ast.Load()),
                    slice=ast.Num(n=0),
                    ctx=ast.Load(),
                ),
            )
            action_result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=MethodInvocation(self.action).to_function_call(
                    action_args, action_keywords
                ),
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
                body=[action_result],
                orelse=[],
            )

            result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=ast.Constant(value=None, kind=None),
            )
            body.append(result)
            body.append(if_check)

        if self.has_post_controller:
            post_controller_call = MethodInvocation(
                self.post_controller
            ).to_function_call()
            body.append(ast.Expr(value=post_controller_call))

        if self.has_action:
            body.append(
                ast.Return(
                    value=ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load())
                )
            )
        else:
            body.append(ast.Return(value=ast.Name(id=CHOSEN_ARG_NAME, ctx=ast.Load())))

        args, saved_defaults = self.get_call_args(
            use_class_arg=True,
            use_k_arg=False,
            use_partition_arg=True,
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
