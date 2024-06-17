import ast
from typing import Any, Callable

from pycontroller2.internal.controlled_method import MethodInvocation
from pycontroller2.internal.exceptions import InvalidControllerMethodError
from pycontroller2.internal.namespace import (
    ACTION_RESULT_ASSIGNMENT_NAME,
    GENERATED_CALL_METHOD_NAME,
    PREFERENCE_CMP_METHOD_NAME,
    PREFERENCE_KEY_METHOD_NAME,
)

from ._base import BaseControllerImplementation


class DoAllImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(cls, name, bases, attrs, stack_frame)

    def validate(self) -> None:
        super().validate()
        if self.has_preference_key and self.has_preference_cmp:
            err = f'DoAll controller "{self.name}" is invalid because both preference methods ("{PREFERENCE_KEY_METHOD_NAME}", and "{PREFERENCE_CMP_METHOD_NAME}") are defined.'
            err += f' You must define only one. Note that "{PREFERENCE_KEY_METHOD_NAME}" is more optimal.'
            raise InvalidControllerMethodError(err)

    def generate_call_method(self) -> Callable[..., Any]:
        body = []

        if self.has_pre_controller:
            pre_controller_call = MethodInvocation(
                self.pre_controller
            ).to_function_call()
            body.append(ast.Expr(value=pre_controller_call))

        if self.has_filter:
            filter_call = MethodInvocation(self.filter).to_function_call()
            # TODO make a call to filter with this

        if self.has_preference_key:
            preference_call = MethodInvocation(self.preference_key).to_function_call()
            # TODO make a nsmallest call here with this

        if self.has_preference_cmp:
            preference_call = MethodInvocation(self.preference_cmp).to_function_call()
            # TODO make a nsmallest call here with this

        if self.has_action:
            result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=MethodInvocation(self.action).to_function_call(),
            )
            body.append(result)

        if self.has_fold:
            fold_call = MethodInvocation(self.fold).to_function_call()
            # TODO pass results of action to the fold

        if self.has_post_controller:
            post_controller_call = MethodInvocation(
                self.post_controller
            ).to_function_call()
            body.append(ast.Expr(value=post_controller_call))

        if self.has_action or self.has_fold:
            body.append(
                ast.Return(
                    value=ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load())
                )
            )

        args, saved_defaults = self.get_call_args(
            use_class_arg=True,
            use_k_arg=False,
            use_partition_arg=True,
            required_action_args=1,
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
