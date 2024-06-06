import ast
from abc import ABC, abstractmethod
from typing import Any, Callable

from pycontroller2.exceptions import InvalidControllerMethod
from pycontroller2.namespace import (
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

        self.__has_pre_controller = (
            self.attrs.get(PRE_CONTROLLER_METHOD_NAME, None) is not None
        )
        self.__has_filter = self.attrs.get(FILTER_METHOD_NAME, None) is not None
        self.__has_preference_key = (
            self.attrs.get(PREFERENCE_KEY_METHOD_NAME, None) is not None
        )
        self.__has_preference_cmp = (
            self.attrs.get(PREFERENCE_CMP_METHOD_NAME, None) is not None
        )
        self.__has_action = self.attrs.get(ACTION_METHOD_NAME, None) is not None
        self.__has_fold = self.attrs.get(FOLD_METHOD_NAME, None) is not None
        self.__has_post_controller = (
            self.attrs.get(POST_CONTROLLER_METHOD_NAME, None) is not None
        )

        self.validate()

    @abstractmethod
    def generate_call_method(self) -> Callable[..., Any]: ...

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

    def validate(self) -> None:
        """
        A pre-validation check of the class attributes, methods, and arguments for the controller.
        This is intended to be a top level check, and more checks are recommended for the derived
        classes.
        """

        if self.has_preference_key and self.has_preference_cmp:
            raise InvalidControllerMethod(
                f'Cannot define both "{PREFERENCE_KEY_METHOD_NAME}" and "{PREFERENCE_CMP_METHOD_NAME}" at the same time. You must choose one or the other.'
            )
