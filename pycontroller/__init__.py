from typing import Any, Iterable

from .internal.metaclass import MetaController as __MetaController


class Controller(metaclass=__MetaController):
    sort_with_key: bool = False
    sort_reverse: bool = False

    def action(self, chosen: Any, *args, **kwargs) -> Any: ...
    def preference(self, a: Any, b: Any, *args, **kwargs) -> int: ...
    def filter(self, chosen: Any, *args, **kwargs) -> bool: ...
    def __call__(self, partition: Iterable, *args, **kwargs) -> Any: ...


# expose only the metaclass wrapper
__all__ = [Controller]
