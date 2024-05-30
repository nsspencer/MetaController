from typing import Any, Iterable, List, Protocol

from .internal.metaclass import MetaController as __MetaController


class Sortable(Protocol):
    """
    Sortable types must support the __lt__ method.
    """

    def __lt__(self, other: "Sortable") -> bool: ...


class Controller(metaclass=__MetaController):
    simple_sort: bool = False
    reverse_sort: bool = False
    fixed_max_chosen: int = None
    dynamic_max_chosen: bool = False
    debug_mode: bool = True

    def action(self, chosen, /, *args, **kwargs) -> Any: ...
    def preference_cmp(self, a, b, /, *args, **kwargs) -> int: ...
    def preference(self, chosen, /, *args, **kwargs) -> Sortable: ...
    def filter(self, chosen, /, *args, **kwargs) -> bool: ...

    if dynamic_max_chosen is True:

        def __call__(
            self, max_chosen: int, partition: Iterable[Any], /, *args, **kwargs
        ) -> List[Any]: ...

    else:

        def __call__(
            self, partition: Iterable[Any], /, *args, **kwargs
        ) -> List[Any]: ...


# expose only the metaclass wrapper
__all__ = [Controller, Sortable]
