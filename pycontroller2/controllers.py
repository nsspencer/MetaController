import inspect
from typing import (
    Any,
    Generic,
    Iterable,
    Protocol,
    TypeAlias,
    TypeVar,
    Union,
    _ProtocolMeta,
)

from .implementation.do import DoImplementation
from .implementation.do_all import DoAllImplementation
from .implementation.do_k import DoKImplementation
from .implementation.do_one import DoOneImplementation

TChosen = TypeVar("TChosen")
TActionReturn = TypeVar("TActionReturn")
TFoldReturn = TypeVar("TFoldReturn")


class SupportsDunderLT(Protocol[TChosen]):
    def __lt__(self, other: TChosen, /, *args: Any, **kwargs: Any) -> bool: ...


class SupportsDunderGT(Protocol[TChosen]):
    def __gt__(self, other: TChosen, /, *args: Any, **kwargs: Any) -> bool: ...


SupportsRichComparison: TypeAlias = SupportsDunderLT | SupportsDunderGT


class MetaController(_ProtocolMeta):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name in ["Do", "DoOne", "DoK", "DoAll"]:
            return

        _base_classes = [base for base in bases if base in [Do, DoOne, DoK, DoAll]]
        if len(_base_classes) > 1:
            raise TypeError("Controller multiple inheritance is not allowed.")
        _base_class = _base_classes[0]

        if _base_class is Do:
            implementation = DoImplementation
        elif _base_class is DoOne:
            implementation = DoOneImplementation
        elif _base_class is DoK:
            implementation = DoKImplementation
        elif _base_class is DoAll:
            implementation = DoAllImplementation
        else:
            raise NotImplementedError("Unkown base class.")  # should not get here

        cls.__call__ = implementation(
            cls, name, bases, attrs, inspect.currentframe().f_back
        ).generate_call_method()


class Do(Generic[TActionReturn], metaclass=MetaController):
    optimize: bool = True
    enable_updates: bool = False

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def action(self, *args: Any, **kwargs: Any) -> TActionReturn: ...

    def post_controller(self, *args: Any, **kwargs: Any) -> None: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(self, *args: Any, **kwargs: Any) -> TActionReturn: ...

    def update_to(self, cls: "Do[TActionReturn]") -> None: ...


class DoOne(Generic[TChosen, TActionReturn], metaclass=MetaController):
    optimize: bool = True
    enable_updates: bool = False
    reverse_preference: bool = False

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def filter(self, chosen: TChosen, *args: Any, **kwargs: Any) -> bool: ...

    def preference_key(
        self, chosen: TChosen, *args: Any, **kwargs: Any
    ) -> SupportsRichComparison: ...

    def preference_cmp(
        self, a: TChosen, b: TChosen, *args: Any, **kwargs: Any
    ) -> int: ...

    def action(self, chosen: TChosen, *args: Any, **kwargs: Any) -> TActionReturn: ...

    def post_controller(self, *args: Any, **kwargs: Any) -> None: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, partition: Iterable[TChosen], /, *args: Any, **kwargs: Any
    ) -> TActionReturn: ...

    def update_to(
        self,
        cls: Union[
            "DoOne[TChosen, TActionReturn]",
            "DoAll[TChosen, TActionReturn, TActionReturn]",
        ],
    ) -> None: ...


class DoK(Generic[TChosen, TActionReturn, TFoldReturn], metaclass=MetaController):
    optimize: bool = True
    enable_updates: bool = False
    reverse_preference: bool = False
    num_threads: None | int = None
    num_processes: None | int = None

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def filter(self, chosen: TChosen, *args: Any, **kwargs: Any) -> bool: ...

    def preference_key(
        self, chosen: TChosen, *args: Any, **kwargs: Any
    ) -> SupportsRichComparison: ...

    def preference_cmp(
        self, a: TChosen, b: TChosen, *args: Any, **kwargs: Any
    ) -> int: ...

    def action(self, chosen: TChosen, *args: Any, **kwargs: Any) -> TActionReturn: ...

    def post_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def fold(
        self, results: Iterable[TActionReturn], *args: Any, **kwargs: Any
    ) -> TFoldReturn: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, k: int, partition: Iterable[TChosen], /, *args: Any, **kwargs: Any
    ) -> Iterable[TActionReturn] | TFoldReturn: ...

    def update_to(self, cls: "DoK[TChosen, TActionReturn, TFoldReturn]") -> None: ...


class DoAll(Generic[TChosen, TActionReturn, TFoldReturn], metaclass=MetaController):
    optimize: bool = True
    enable_updates: bool = False
    reverse_preference: bool = False
    num_threads: None | int = None
    num_processes: None | int = None

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def filter(self, chosen: TChosen, *args: Any, **kwargs: Any) -> bool: ...

    def preference_key(
        self, chosen: TChosen, *args: Any, **kwargs: Any
    ) -> SupportsRichComparison: ...

    def preference_cmp(
        self, a: TChosen, b: TChosen, *args: Any, **kwargs: Any
    ) -> int: ...

    def action(self, chosen: TChosen, *args: Any, **kwargs: Any) -> TActionReturn: ...

    def post_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def fold(
        self, results: Iterable[TActionReturn], *args: Any, **kwargs: Any
    ) -> TFoldReturn: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, partition: Iterable[TChosen], /, *args: Any, **kwargs: Any
    ) -> Iterable[TActionReturn] | TFoldReturn: ...

    def update_to(
        self,
        cls: Union[
            "DoAll[TChosen, TActionReturn, TFoldReturn]",
            "DoOne[TChosen, TActionReturn, TFoldReturn]",
        ],
    ) -> None: ...
