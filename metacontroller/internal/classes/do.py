import ast
import warnings
from typing import Any, Callable

from metacontroller.internal.method_invocation import MethodInvocation
from metacontroller.internal.namespace import (
    ACTION_METHOD_NAME,
    ACTION_RESULT_ASSIGNMENT_NAME,
    GENERATED_CALL_METHOD_NAME,
    POST_CONTROLLER_METHOD_NAME,
    PRE_CONTROLLER_METHOD_NAME,
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
            sort_key_enabled=False,
            sort_cmp_enabled=False,
            fold_enabled=False,
        )

    def validate(self) -> None:
        super().validate()
        if self.has_filter:
            warnings.warn(
                "Filter is not supported for Do controllers. It will be ignored."
            )

        if self.has_sort_cmp or self.has_sort_key:
            warnings.warn(
                "Sorting is not supported for Do controllers. It will be ignored."
            )

        if self.has_fold:
            warnings.warn(
                "Fold is not supported for Do controllers. It will be ignored."
            )

    def generate_call_method(self) -> Callable[..., Any]:
        body = []

        if self.has_pre_controller:
            pre_controller_call = MethodInvocation(
                self.pre_controller
            ).to_function_call(name=PRE_CONTROLLER_METHOD_NAME)
            body.append(ast.Expr(value=pre_controller_call))

        if self.has_action:
            result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=MethodInvocation(self.action).to_function_call(
                    name=ACTION_METHOD_NAME
                ),
            )
            body.append(result)

        if self.has_post_controller:
            post_controller_call = MethodInvocation(
                self.post_controller
            ).to_function_call(name=POST_CONTROLLER_METHOD_NAME)
            body.append(ast.Expr(value=post_controller_call))

        if self.has_action:
            body.append(
                ast.Return(
                    value=ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load())
                )
            )

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
