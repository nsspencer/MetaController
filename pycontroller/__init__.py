from . import quicksort
from .internal.metaclass import MetaController as __MetaController


class Controller(metaclass=__MetaController): ...


# expose only the metaclass wrapper
__all__ = [Controller, quicksort]
