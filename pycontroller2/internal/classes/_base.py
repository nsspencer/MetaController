import ast
from abc import ABC, abstractmethod
from typing import Any, Callable

from pycontroller2.internal.exceptions import InvalidControllerMethod
from pycontroller2.internal.namespace import (
    ACTION_METHOD_NAME,
    FILTER_METHOD_NAME,
    FOLD_METHOD_NAME,
    GENERATED_CALL_METHOD_NAME,
    POST_CONTROLLER_METHOD_NAME,
    PRE_CONTROLLER_METHOD_NAME,
    PREFERENCE_CMP_METHOD_NAME,
    PREFERENCE_KEY_METHOD_NAME,
)


class BaseControllerImplementation(ABC):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__()
        self.cls = cls
        self.name = name
        self.bases = bases
        self.attrs = attrs
        self.stack_frame = stack_frame

        self.__has_pre_controller = self.get_pre_controller_attr() is not None
        self.__has_filter = self.get_filter_attr() is not None
        self.__has_preference_key = self.get_preference_key_attr() is not None
        self.__has_preference_cmp = self.get_preference_cmp_attr() is not None
        self.__has_action = self.get_action_attr() is not None
        self.__has_fold = self.get_fold_attr() is not None
        self.__has_post_controller = self.get_post_controller_attr() is not None

    ####
    # Methods to be defined by sub-classes

    @abstractmethod
    def validate(self) -> None:
        """
        Validation method to ensure that class attributes and method signatures/return values
        are all valid before any compilation is done. This method should raise specific
        exceptions if a controller is deemed invalid.
        """
        ...

    @abstractmethod
    def generate_call_method(self) -> Callable[..., Any]:
        """
        Delegate to each controller implementation to create its own call method.
        This must return a callable method that will be bound to the classes __call__
        dunder method. Each instance will be callable with the output of this method.

        Returns:
            Callable[..., Any]: __call__() method for the controller instances.
        """
        ...

    ####
    # Read only properties

    @property
    def has_pre_controller(self) -> bool:
        return self.__has_pre_controller

    @property
    def has_filter(self) -> bool:
        return self.__has_filter

    @property
    def has_preference_key(self) -> bool:
        return self.__has_preference_key

    @property
    def has_preference_cmp(self) -> bool:
        return self.__has_preference_cmp

    @property
    def has_action(self) -> bool:
        return self.__has_action

    @property
    def has_fold(self) -> bool:
        return self.__has_fold

    @property
    def has_post_controller(self) -> bool:
        return self.__has_post_controller

    ####
    # Common helpers

    def compile_call_method(
        self, module: ast.Module, additional_globals: dict = None
    ) -> Callable[..., Any]:
        """
        Compiles the call method from within the passed in module for this controller.

        Args:
            module (ast.Module): module which contains the call function.
            additional_globals (dict, optional): additional global values to include in compilation. Defaults to None.

        Returns:
            Callable[..., Any]: generated call method for this controller.
        """
        _globals = self.stack_frame.f_globals
        _globals.update(self.stack_frame.f_locals)
        if additional_globals is not None:
            _globals.update(additional_globals)

        _locals = {}
        eval(
            compile(module, filename="<ast>", mode="exec"),
            _globals,
            _locals,
        )
        return _locals[GENERATED_CALL_METHOD_NAME]

    def get_pre_controller_attr(self) -> Callable:
        return self.attrs.get(PRE_CONTROLLER_METHOD_NAME, None)

    def get_filter_attr(self) -> Callable:
        return self.attrs.get(FILTER_METHOD_NAME, None)

    def get_preference_key_attr(self) -> Callable:
        return self.attrs.get(PREFERENCE_KEY_METHOD_NAME, None)

    def get_preference_cmp_attr(self) -> Callable:
        return self.attrs.get(PREFERENCE_CMP_METHOD_NAME, None)

    def get_action_attr(self) -> Callable:
        return self.attrs.get(ACTION_METHOD_NAME, None)

    def get_fold_attr(self) -> Callable:
        return self.attrs.get(FOLD_METHOD_NAME, None)

    def get_post_controller_attr(self) -> Callable:
        return self.attrs.get(POST_CONTROLLER_METHOD_NAME, None)
