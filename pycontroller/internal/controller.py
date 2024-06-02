from typing import Any, Iterable, List, Protocol, TypeAlias, TypeVar

from .metaclass import MetaController as __MetaController

# type hints taken from pylance .pyi tpye hints

_T_contra = TypeVar("_T_contra", contravariant=True)


class SupportsDunderLT(Protocol[_T_contra]):
    def __lt__(self, other: _T_contra, /) -> bool: ...


class SupportsDunderGT(Protocol[_T_contra]):
    def __gt__(self, other: _T_contra, /) -> bool: ...


SupportsRichComparison: TypeAlias = SupportsDunderLT[Any] | SupportsDunderGT[Any]


class Controller(metaclass=__MetaController):
    sort: bool = False
    sort_reverse: bool = False
    fixed_max_chosen: int = None
    dynamic_max_chosen: bool = False
    optimize: bool = True

    def action(self, chosen, /, *args, **kwargs) -> Any: ...
    def sort_cmp(self, a, b, /, *args, **kwargs) -> int: ...
    def sort_key(self, chosen, /, *args, **kwargs) -> SupportsRichComparison: ...
    def filter(self, chosen, /, *args, **kwargs) -> bool: ...

    if dynamic_max_chosen is True:

        def __call__(
            self, max_chosen: int, partition: Iterable[Any], /, *args, **kwargs
        ) -> List[Any]: ...

    else:

        def __call__(
            self, partition: Iterable[Any], /, *args, **kwargs
        ) -> List[Any]: ...
