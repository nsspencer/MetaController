import ast
import warnings
from typing import Any, Callable

from pycontroller2.internal.methods import Action, PostController, PreController

from ._base import BaseControllerImplementation


class DoImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(cls, name, bases, attrs, stack_frame)

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

        if self.has_pre_controller:
            pre_controller = PreController(self.get_pre_controller_attr())

        if self.has_action:
            action = Action(self.get_action_attr())

        if self.has_post_controller:
            post_controller = PostController(self.get_post_controller_attr())

        module = ast.Module(body=body, type_ignores=[])
        return self.compile_call_method(module)
