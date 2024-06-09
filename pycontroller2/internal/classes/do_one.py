import ast
from typing import Any, Callable

from ._base import BaseControllerImplementation


class DoOneImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(cls, name, bases, attrs, stack_frame)

    def validate(self) -> None:
        return super().validate()

    def generate_call_method(self) -> Callable[..., Any]:
        pass  # TODO
