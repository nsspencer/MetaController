import ast
from typing import Callable

from pycontroller.internal.methods.base_method import BaseControlledMethod


class Action(BaseControlledMethod):

    def __init__(self, fn: Callable) -> None:
        super().__init__(fn)

    def is_compatible_with(self, other: "Action") -> bool:
        if not isinstance(other, Action):
            return False

        # TODO: actually check things...
        return True

    def to_module(self) -> ast.Module:
        # if has no arguments other than "chosen"
        # setup_statements.append("action_fn = action")
        # action_fn(chosen)

        # if has other arguments
        pass

    def __eq__(self, other: "Action") -> bool:
        return self.is_compatible_with(other)

    def __ne__(self, other: "Action") -> bool:
        return not self.is_compatible_with(other)
