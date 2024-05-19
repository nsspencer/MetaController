from typing import Any, Iterable

from .internal.metaclass import MetaController as __MetaController


class Controller(metaclass=__MetaController):
    sort_with_key: bool = False
    sort_reverse: bool = False
    fixed_max_chosen: int = None
    dynamic_max_chosen: bool = False

    def action(self, chosen: Any, *args, **kwargs) -> Any: ...
    def preference(self, a: Any, b: Any, *args, **kwargs) -> int: ...
    def filter(self, chosen: Any, *args, **kwargs) -> bool: ...

    if dynamic_max_chosen is True:

        def __call__(
            self, max_chosen: int, partition: Iterable, *args, **kwargs
        ) -> Any: ...

    else:

        def __call__(self, partition: Iterable, *args, **kwargs) -> Any: ...


# expose only the metaclass wrapper
__all__ = [Controller]
