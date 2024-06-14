import ast
import warnings
from typing import Any, Callable

from pycontroller2.internal.controlled_method import MethodInvocation
from pycontroller2.internal.namespace import (
    ACTION_RESULT_ASSIGNMENT_NAME,
    GENERATED_CALL_METHOD_NAME,
)

from ._base import BaseControllerImplementation


class DoImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(
            cls,
            name,
            bases,
            attrs,
            stack_frame,
            filter_enabled=False,
            preference_key_enabled=False,
            preference_cmp_enabled=False,
            fold_enabled=False,
        )

    def validate(self) -> None:
        if self.has_filter:
            warnings.warn(
                "Filter is not supported for Do controllers. It will be ignored."
            )

        if self.has_preference_cmp or self.has_preference_key:
            warnings.warn(
                "Preference is not supported for Do controllers. It will be ignored."
            )

        if self.has_fold:
            warnings.warn(
                "Fold is not supported for Do controllers. It will be ignored."
            )

    def generate_call_method(self) -> Callable[..., Any]:
        body = []
        lineno = 1

        if self.has_pre_controller:
            pre_controller_call = MethodInvocation(
                self.pre_controller
            ).to_function_call()
            body.append(ast.Expr(value=pre_controller_call))
            lineno += 1

        if self.has_action:
            result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=MethodInvocation(self.action).to_function_call(),
            )
            body.append(result)
            lineno += 1

        if self.has_post_controller:
            post_controller_call = MethodInvocation(
                self.post_controller
            ).to_function_call()
            body.append(ast.Expr(value=post_controller_call))
            lineno += 1

        if self.has_action:
            body.append(
                ast.Return(
                    value=ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load())
                )
            )
            lineno += 1

        args, saved_defaults = self.get_call_args(
            use_class_arg=True,
            use_k_arg=False,
            use_partition_arg=False,
            required_action_args=0,
        )
        call_fn = ast.FunctionDef(
            name=GENERATED_CALL_METHOD_NAME,
            args=args,
            body=body,
            decorator_list=[],
            type_params=[],
        )

        module = ast.fix_missing_locations(ast.Module(body=[call_fn], type_ignores=[]))
        return self.compile_call_method(module, saved_defaults)
