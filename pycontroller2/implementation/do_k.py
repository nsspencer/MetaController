import ast
from typing import Any, Callable

from .base import BaseControllerImplementation


class DoKImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(cls, name, bases, attrs, stack_frame)

    def generate_call_method(self) -> Callable[..., Any]:
        pass  # TODO
