from typing import Iterable, List, Protocol, TypeVar

from .internal.metaclass import MetaController as __MetaController


class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool: ...


Chosen = TypeVar("Chosen")
AnyReturn = TypeVar("AnyReturn")


class Controller(metaclass=__MetaController):
    simple_sort: bool = False
    reverse_sort: bool = False
    fixed_max_chosen: int = None
    dynamic_max_chosen: bool = False
    debug_mode: bool = True

    def action(self, chosen: Chosen, *args, **kwargs) -> AnyReturn: ...
    def preference_cmp(self, a: Chosen, b: Chosen, *args, **kwargs) -> int: ...
    def preference(self, chosen: Chosen, *args, **kwargs) -> Comparable: ...
    def filter(self, chosen: Chosen, *args, **kwargs) -> bool: ...

    if dynamic_max_chosen is True:

        def __call__(
            self, max_chosen: int, partition: Iterable[Chosen], *args, **kwargs
        ) -> List[AnyReturn]: ...

    else:

        def __call__(
            self, partition: Iterable[Chosen], *args, **kwargs
        ) -> List[AnyReturn]: ...


# expose only the metaclass wrapper
__all__ = [Controller, Comparable, Chosen, AnyReturn]
