import ast
from abc import ABC, abstractmethod
from typing import Callable


class BaseControlledMethod(ABC):

    def __init__(self, fn: Callable) -> None:
        super().__init__()
        if not callable(fn):
            raise ValueError(
                "BaseControlledMethod initializer requires a callable function."
            )
        self.fn = fn

    @abstractmethod
    def is_compatible_with(self, other: "BaseControlledMethod") -> bool:
        pass

    @abstractmethod
    def to_module(self) -> ast.Module:
        pass

    def __eq__(self, other: "BaseControlledMethod") -> bool:
        return self.is_compatible_with(other)

    def __ne__(self, other: "BaseControlledMethod") -> bool:
        return not self.is_compatible_with(other)
