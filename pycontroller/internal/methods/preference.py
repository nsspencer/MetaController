import ast
from typing import Callable

from pycontroller.internal.methods.base_method import BaseControlledMethod


class Preference(BaseControlledMethod):

    def __init__(self, fn: Callable) -> None:
        super().__init__(fn)

    def is_compatible_with(self, other: "Preference") -> bool:
        if not isinstance(other, Preference):
            return False

        # TODO: actually check things...
        return True

    def to_module(self) -> ast.Module:
        pass

    def __eq__(self, other: "Preference") -> bool:
        return self.is_compatible_with(other)

    def __ne__(self, other: "Preference") -> bool:
        return not self.is_compatible_with(other)
