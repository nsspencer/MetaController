import ast
from typing import Callable

from pycontroller.internal.methods.base_method import BaseControlledMethod


class Filter(BaseControlledMethod):

    def __init__(self, fn: Callable) -> None:
        super().__init__(fn)

    def is_compatible_with(self, other: "Filter") -> bool:
        if not isinstance(other, Filter):
            return False

        # TODO: actually check things...
        return True

    def to_module(self) -> ast.Module:
        pass

    def __eq__(self, other: "Filter") -> bool:
        return self.is_compatible_with(other)

    def __ne__(self, other: "Filter") -> bool:
        return not self.is_compatible_with(other)
