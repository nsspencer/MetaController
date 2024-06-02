from typing import Any, Iterable, List, Protocol

from .metaclass import MetaController as __MetaController


class SortableType(Protocol):
    """
    SortableType types must support the __lt__ method.
    """

    def __lt__(self, other: "SortableType") -> bool: ...


55


class Controller(metaclass=__MetaController):
    sort: bool = False
    sort_reverse: bool = False
    fixed_max_chosen: int = None
    dynamic_max_chosen: bool = False
    optimize: bool = True

    def action(self, chosen, /, *args, **kwargs) -> Any: ...
    def sort_cmp(self, a, b, /, *args, **kwargs) -> int: ...
    def sort_key(self, chosen, /, *args, **kwargs) -> SortableType: ...
    def filter(self, chosen, /, *args, **kwargs) -> bool: ...

    if dynamic_max_chosen is True:

        def __call__(
            self, max_chosen: int, partition: Iterable[Any], /, *args, **kwargs
        ) -> List[Any]: ...

    else:

        def __call__(
            self, partition: Iterable[Any], /, *args, **kwargs
        ) -> List[Any]: ...
