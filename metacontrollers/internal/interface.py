import inspect
from typing import Any, Generic, Iterable, List, Protocol, TypeVar, Union, _ProtocolMeta

from .classes.do import DoImplementation
from .classes.do_all import DoAllImplementation
from .classes.do_k import DoKImplementation
from .classes.do_one import DoOneImplementation

TChosen = TypeVar("TChosen")
TActionReturn = TypeVar("TActionReturn")
TFoldReturn = TypeVar("TFoldReturn")
TSupportsRichComparison = TypeVar(
    "TSupportsRichComparison", bound="SupportsRichComparison"
)


class SupportsRichComparison(Protocol):
    def __lt__(self, other: TSupportsRichComparison) -> bool: ...
    def __gt__(self, other: TSupportsRichComparison) -> bool: ...


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

        controller = implementation(
            cls, name, bases, attrs, inspect.currentframe().f_back
        )
        controller.validate()
        cls.__call__ = controller.generate_call_method()


class Do(Generic[TActionReturn], metaclass=MetaController):
    optimize: bool = False

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self) -> None: ...

    def action(self) -> TActionReturn: ...

    def post_controller(self) -> None: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(self, *args: Any, **kwargs: Any) -> Union[TActionReturn, None]:
        """Generated call method for your controller. *args and **kwargs represent the
        position only, arguments, defaulted arguments, argument unpacks, keyword only,
        and keyword unpacks that you have defined (if any) across all your controlled
        methods.

        Returns:
            TActionReturn: If your action returns a value, that will be the return, else
            this method will return None.
        """
        ...

    def update_to(self, cls: "Do[TActionReturn]") -> None: ...


class DoOne(Generic[TChosen, TActionReturn], metaclass=MetaController):
    optimize: bool = False
    reverse_sort: bool = False

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self) -> None: ...

    def filter(self, chosen: TChosen) -> bool: ...

    def sort_key(self, chosen: TChosen) -> SupportsRichComparison: ...

    def sort_cmp(self, a: TChosen, b: TChosen) -> int: ...

    def action(self, chosen: TChosen) -> TActionReturn: ...

    def post_controller(self) -> None: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, partition: Iterable[TChosen], /, *args: Any, **kwargs: Any
    ) -> Union[TActionReturn, None]:
        """Generated call method for your controller. *args and **kwargs represent the
        position only, arguments, defaulted arguments, argument unpacks, keyword only,
        and keyword unpacks that you have defined (if any) across all your controlled
        methods.

        Args:
            partition (Iterable[TChosen]): Iterable representing the set of elements
            this controller will operate over.

        Returns:
            TActionReturn: If your action returns a value, that will be the return, else
            this method will return None.
        """
        ...

    def update_to(
        self,
        cls: Union[
            "DoOne[TChosen, TActionReturn]",
            "DoAll[TChosen, TActionReturn, TActionReturn]",
        ],
    ) -> None: ...


class DoK(Generic[TChosen, TActionReturn, TFoldReturn], metaclass=MetaController):
    optimize: bool = False
    reverse_sort: bool = False

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self) -> None: ...

    def filter(self, chosen: TChosen) -> bool: ...

    def sort_key(self, chosen: TChosen) -> SupportsRichComparison: ...

    def sort_cmp(self, a: TChosen, b: TChosen) -> int: ...

    def action(self, chosen: TChosen) -> TActionReturn: ...

    def post_controller(self) -> None: ...

    def fold(self, results: List[TActionReturn]) -> TFoldReturn: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, k: int, partition: Iterable[TChosen], /, *args: Any, **kwargs: Any
    ) -> Union[Iterable[TActionReturn], TFoldReturn, None]:
        """Generated call method for your controller. *args and **kwargs represent the
        position only, arguments, defaulted arguments, argument unpacks, keyword only,
        and keyword unpacks that you have defined (if any) across all your controlled
        methods.

        Args:
            k (int): Number of chosen elements to operate over from the partition.
            partition (Iterable[TChosen]): Iterable representing the set of elements
            this controller will operate over.

        Returns:
            Union[Iterable[TActionReturn], TFoldReturn, None]: If action returns a value and there
            is no fold(...) method defined, the result will be an Iterable of elements
            returned from k number of calls to the action(...). If fold(...) is defined,
            this will return the result from the fold(...) method. Else, this will return
            None.
        """
        ...

    def update_to(self, cls: "DoK[TChosen, TActionReturn, TFoldReturn]") -> None: ...


class DoAll(Generic[TChosen, TActionReturn, TFoldReturn], metaclass=MetaController):
    optimize: bool = False
    reverse_sort: bool = False

    ###
    # Valid User Defined Methods:
    #

    def pre_controller(self) -> None: ...

    def filter(self, chosen: TChosen) -> bool: ...

    def sort_key(self, chosen: TChosen) -> SupportsRichComparison: ...

    def sort_cmp(self, a: TChosen, b: TChosen) -> int: ...

    def action(self, chosen: TChosen) -> TActionReturn: ...

    def post_controller(self) -> None: ...

    def fold(self, results: List[TActionReturn]) -> TFoldReturn: ...

    ###
    # Built-in Instance Methods
    #

    def __call__(
        self, partition: Iterable[TChosen], /, *args: Any, **kwargs: Any
    ) -> Union[Iterable[TActionReturn], TFoldReturn, None]:
        """Generated call method for your controller. *args and **kwargs represent the
        position only, arguments, defaulted arguments, argument unpacks, keyword only,
        and keyword unpacks that you have defined (if any) across all your controlled
        methods.

        Args:
            partition (Iterable[TChosen]): Iterable representing the set of elements
            this controller will operate over.

        Returns:
            Union[Iterable[TActionReturn], TFoldReturn, None]: If action returns a value and there
            is no fold(...) method defined, the result will be an Iterable of elements
            returned from all the calls to the action(...) method. If fold(...) is defined,
            this will return the result from the fold(...) method. Else, this will return
            None.
        """
        ...

    def update_to(
        self,
        cls: Union[
            "DoAll[TChosen, TActionReturn, TFoldReturn]",
            "DoOne[TChosen, TActionReturn, TFoldReturn]",
        ],
    ) -> None: ...
