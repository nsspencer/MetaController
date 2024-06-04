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

        _base_cls = bases[0]
        if _base_cls is Do:
            pass
        elif _base_cls is DoOne:
            pass
        elif _base_cls is DoK:
            pass
        elif _base_cls is DoAll:
            pass
        else:
            raise NotImplementedError("Unkown base class.")

        pass


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
        self, partition: Iterable[TChosen], *args: Any, **kwargs: Any
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

    def continue_while(
        self, action_result: TActionReturn, *args: Any, **kwargs: Any
    ) -> bool: ...

    def post_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def fold(
        self, results: Iterable[TActionReturn], *args: Any, **kwargs: Any
    ) -> TFoldReturn: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, k: int, partition: Iterable[TChosen], *args: Any, **kwargs: Any
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

    def continue_while(
        self, action_result: TActionReturn, *args: Any, **kwargs: Any
    ) -> bool: ...

    def post_controller(self, *args: Any, **kwargs: Any) -> None: ...

    def fold(
        self, results: Iterable[TActionReturn], *args: Any, **kwargs: Any
    ) -> TFoldReturn: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, partition: Iterable[TChosen], *args: Any, **kwargs: Any
    ) -> Iterable[TActionReturn] | TFoldReturn: ...

    def update_to(
        self,
        cls: Union[
            "DoAll[TChosen, TActionReturn, TFoldReturn]",
            "DoOne[TChosen, TActionReturn, TFoldReturn]",
        ],
    ) -> None: ...
