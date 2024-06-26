import ast
from abc import ABC, abstractmethod
from textwrap import dedent
from typing import Any, Callable, Dict, List, Tuple, Union

from metacontroller.internal.exceptions import (
    ArgumentError,
    InvalidControllerMethodError,
)
from metacontroller.internal.method_inspector import MethodInspector
from metacontroller.internal.namespace import (
    ACTION_METHOD_NAME,
    CLASS_ARG_NAME,
    FILTER_METHOD_NAME,
    FOLD_METHOD_NAME,
    GENERATED_CALL_METHOD_NAME,
    K_ARG_NAME,
    PARTITION_ARG_NAME,
    POST_CONTROLLER_METHOD_NAME,
    PRE_CONTROLLER_METHOD_NAME,
    SORT_CMP_METHOD_NAME,
    SORT_KEY_METHOD_NAME,
)


class BaseControllerImplementation(ABC):
    def __init__(
        self,
        cls,
        name,
        bases,
        attrs,
        stack_frame,
        pre_controller_enabled: bool = True,
        filter_enabled: bool = True,
        sort_key_enabled: bool = True,
        sort_cmp_enabled: bool = True,
        action_enabled: bool = True,
        fold_enabled: bool = True,
        post_controller_enabled: bool = True,
    ) -> None:
        super().__init__()
        self.cls = cls
        self.name = name
        self.bases = bases
        self.attrs = attrs
        self.stack_frame = stack_frame

        self.__pre_controller = (
            MethodInspector(self.attrs[PRE_CONTROLLER_METHOD_NAME])
            if PRE_CONTROLLER_METHOD_NAME in self.attrs and pre_controller_enabled
            else None
        )

        self.__filter = (
            MethodInspector(self.attrs[FILTER_METHOD_NAME])
            if FILTER_METHOD_NAME in self.attrs and filter_enabled
            else None
        )

        self.__sort_key = (
            MethodInspector(self.attrs[SORT_KEY_METHOD_NAME])
            if SORT_KEY_METHOD_NAME in self.attrs and sort_key_enabled
            else None
        )

        self.__sort_cmp = (
            MethodInspector(self.attrs[SORT_CMP_METHOD_NAME])
            if SORT_CMP_METHOD_NAME in self.attrs and sort_cmp_enabled
            else None
        )

        self.__action = (
            MethodInspector(self.attrs[ACTION_METHOD_NAME])
            if ACTION_METHOD_NAME in self.attrs and action_enabled
            else None
        )

        self.__fold = (
            MethodInspector(self.attrs[FOLD_METHOD_NAME])
            if FOLD_METHOD_NAME in self.attrs and fold_enabled
            else None
        )

        self.__post_controller = (
            MethodInspector(self.attrs[POST_CONTROLLER_METHOD_NAME])
            if POST_CONTROLLER_METHOD_NAME in self.attrs and post_controller_enabled
            else None
        )

    ####
    # Methods to be defined by sub-classes

    @abstractmethod
    def validate(self) -> None:
        """
        Validation method to ensure that class attributes and method signatures/return values
        are all valid before any compilation is done. This method should raise specific
        exceptions if a controller is deemed invalid.
        """
        # assert there is some sort of controlled method in the controller
        if (
            not self.has_pre_controller
            and not self.has_filter
            and not self.has_sort_key
            and not self.has_sort_cmp
            and not self.has_action
            and not self.has_fold
            and not self.has_post_controller
        ):
            raise InvalidControllerMethodError(
                f'"{self.name}" must have at least one controlled method to be valid.'
            )

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
        return self.__pre_controller is not None

    @property
    def pre_controller(self) -> Union[MethodInspector, None]:
        return self.__pre_controller

    @property
    def has_filter(self) -> bool:
        return self.__filter is not None

    @property
    def filter(self) -> Union[MethodInspector, None]:
        return self.__filter

    @property
    def has_sort_key(self) -> bool:
        return self.__sort_key is not None

    @property
    def sort_key(self) -> Union[MethodInspector, None]:
        return self.__sort_key

    @property
    def has_sort_cmp(self) -> bool:
        return self.__sort_cmp is not None

    @property
    def sort_cmp(self) -> Union[MethodInspector, None]:
        return self.__sort_cmp

    @property
    def has_action(self) -> bool:
        return self.__action is not None

    @property
    def action(self) -> Union[MethodInspector, None]:
        return self.__action

    @property
    def has_fold(self) -> bool:
        return self.__fold is not None

    @property
    def fold(self) -> Union[MethodInspector, None]:
        return self.__fold

    @property
    def has_post_controller(self) -> bool:
        return self.__post_controller is not None

    @property
    def post_controller(self) -> Union[MethodInspector, None]:
        return self.__post_controller

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

    def get_call_args(
        self,
        use_class_arg: bool = True,
        use_k_arg: bool = False,
        use_partition_arg: bool = True,
        required_pre_controller_args: int = 0,
        required_filter_args: int = 1,
        required_sort_key_args: int = 1,
        required_sort_cmp_args: int = 2,
        required_action_args: int = 1,
        requried_fold_args: int = 1,
        required_post_controller_args: int = 0,
    ) -> Tuple[ast.arguments, dict]:
        """
        The goal of this function is to determine the set of parameters that make up the call method
        of this controller. This is done by inspecting the paramters of the controlled methods
        that are a part of this controller.

        Position only and non-defaulted keyword arguments are required to share the same name.

        Keyword only and default arguments are allowed to shared the same name, but they must also
        share the same default argument. Duplicated keywords with different default values
        are invalid, and an error will be thrown.

        Variable args are supported, but any controlled method that uses them will be required to use
        the same vararg name.

        Kwargs are supported, but any controlled method that uses them will be required to use
        the same kwarg name.

        Raises:
            AttributeError: for duplicate keyword/default IDs without the same default value.

        Returns:
            Tuple[ast.arguments, dict]: A tuple containing the Arguments for the generated call method, as
            well as a dictionary of the saved argument defaults that should be passed to the compile method.
        """
        # arguments to be used when constructing the resulting ast.arguments
        posonlyargs = []
        args = []
        kwonlyargs = []
        kw_defaults = []
        defaults = []
        var_arg = None
        kwarg = None
        saved_defaults = {}

        if use_class_arg:
            # add the class argument
            posonlyargs.append(
                ast.arg(arg=CLASS_ARG_NAME, annotation=None, type_comment=None)
            )

        if use_k_arg:
            # add the dynamic_max_chosen K argument
            posonlyargs.append(
                ast.arg(arg=K_ARG_NAME, annotation=None, type_comment=None)
            )

        if use_partition_arg:
            # add the partition argument
            posonlyargs.append(
                ast.arg(arg=PARTITION_ARG_NAME, annotation=None, type_comment=None)
            )

        # join the positional and non-defaulted arguments from the controlled methods
        pre_controller_args = []
        if self.has_pre_controller:
            arg_start_index = 0 if self.pre_controller.is_staticmethod else 1
            arg_start_index += required_pre_controller_args
            pre_controller_args = self.pre_controller.get_non_defaulted_args()[
                arg_start_index:
            ]

        filter_args = []
        if self.has_filter:
            arg_start_index = 0 if self.filter.is_staticmethod else 1
            arg_start_index += required_filter_args
            filter_args = self.filter.get_non_defaulted_args()[arg_start_index:]

        sort_key_args = []
        if self.has_sort_key:
            arg_start_index = 0 if self.sort_key.is_staticmethod else 1
            arg_start_index += required_sort_key_args
            sort_key_args = self.sort_key.get_non_defaulted_args()[arg_start_index:]

        sort_cmp_args = []
        if self.has_sort_cmp:
            arg_start_index = 0 if self.sort_cmp.is_staticmethod else 1
            arg_start_index += required_sort_cmp_args
            sort_cmp_args = self.sort_cmp.get_non_defaulted_args()[arg_start_index:]

        action_args = []
        if self.has_action:
            arg_start_index = 0 if self.action.is_staticmethod else 1
            arg_start_index += required_action_args
            action_args = self.action.get_non_defaulted_args()[arg_start_index:]

        fold_args = []
        if self.has_fold:
            arg_start_index = 0 if self.fold.is_staticmethod else 1
            arg_start_index += requried_fold_args
            fold_args = self.fold.get_non_defaulted_args()[arg_start_index:]

        post_controller_args = []
        if self.has_post_controller:
            arg_start_index = 0 if self.post_controller.is_staticmethod else 1
            arg_start_index += required_post_controller_args
            post_controller_args = self.post_controller.get_non_defaulted_args()[
                arg_start_index:
            ]

        max_args = max(
            len(pre_controller_args),
            len(filter_args),
            len(sort_key_args),
            len(sort_cmp_args),
            len(action_args),
            len(fold_args),
            len(post_controller_args),
        )

        # check each non-defaulted argument in each index and ensure its the same argument name
        shared_msg = "Shared positional arguments must have the same name across all controlled methods that use it."
        for index in range(0, max_args, 1):
            current_arg: Union[str, None] = None
            if len(pre_controller_args) > index:
                current_arg = pre_controller_args[index]

            if len(filter_args) > index:
                if current_arg is None:
                    current_arg = filter_args[index]
                elif current_arg != filter_args[index]:
                    msg = f'{FILTER_METHOD_NAME} argument {index} "{filter_args[index]}" is positionally shared with "{current_arg}"; choose one name for this argument.'
                    msg += shared_msg
                    raise ArgumentError(msg)

            if len(sort_key_args) > index:
                if current_arg is None:
                    current_arg = sort_key_args[index]
                elif current_arg != sort_key_args[index]:
                    msg = f'{SORT_KEY_METHOD_NAME} argument {index} "{sort_key_args[index]}" is positionally shared with "{current_arg}"; choose one name for this argument. '
                    msg += shared_msg
                    raise ArgumentError(msg)

            if len(sort_cmp_args) > index:
                if current_arg is None:
                    current_arg = sort_cmp_args[index]
                elif current_arg != sort_cmp_args[index]:
                    msg = f'{SORT_CMP_METHOD_NAME} argument {index} "{sort_cmp_args[index]}" is positionally shared with "{current_arg}"; choose one name for this argument. '
                    msg += shared_msg
                    raise ArgumentError(msg)

            if len(action_args) > index:
                if current_arg is None:
                    current_arg = action_args[index]
                elif current_arg != action_args[index]:
                    msg = f'{ACTION_METHOD_NAME} argument {index} "{action_args[index]}" is positionally shared with "{current_arg}"; choose one name for this argument. '
                    msg += shared_msg
                    raise ArgumentError(msg)

            if len(fold_args) > index:
                if current_arg is None:
                    current_arg = fold_args[index]
                elif current_arg != fold_args[index]:
                    msg = f'{FOLD_METHOD_NAME} argument {index} "{fold_args[index]}" is positionally shared with "{current_arg}"; choose one name for this argument. '
                    msg += shared_msg
                    raise ArgumentError(msg)

            if len(post_controller_args) > index:
                if current_arg is None:
                    current_arg = post_controller_args[index]
                elif current_arg != post_controller_args[index]:
                    msg = f'{POST_CONTROLLER_METHOD_NAME} argument {index} "{post_controller_args[index]}" is positionally shared with "{current_arg}"; choose one name for this argument. '
                    msg += shared_msg
                    raise ArgumentError(msg)

            if current_arg is not None:
                args.append(ast.arg(arg=current_arg, annotation=None))

        # defined as an inner function to pass args and saved_global_kwargs into the namespace
        def _should_include_arg(
            keyword: str,
            default: Any,
            existing_args: List[str],
            saved_global_kwargs: Dict[str, Any] = saved_defaults,
        ) -> bool:
            """
            Checks if a keyword argument already exists with the same default value. If it exists,
            return False since the keyword argument is already taken care of. If it does not exist,
            return True since it should be added. If the keyword argument exists and has a different
            (decided by == (__eq__) operator) default value, raise an exception because they must be
            the same default.

            Args:
                keyword (str): keyword argument in question
                default (Any): default value for the keyword in question
                existing_args (List[str]): arguments that have already been added.
                saved_global_kwargs (Dict[str, Any], optional): saved defaults. Defaults to self.saved_global_kwargs.

            Raises:
                AttributeError: Duplicate keyword arguments must have equivalent default values.

            Returns:
                bool: Should include in args list
            """
            if keyword in existing_args:
                _ctrl_keyword_name = f"{keyword}"
                if _ctrl_keyword_name in saved_global_kwargs:
                    val = saved_global_kwargs[_ctrl_keyword_name]
                if default == val:
                    return False
                else:
                    raise AttributeError(
                        dedent(
                            f'Duplicate keyword argument "{keyword}" with different default values.\
                            Shared keyword arguments must have the same default value.\
                                Equality is checked with the __eq__ operator.'
                        )
                    )
            return True

        def add_non_conflicting_parameters(
            keyword_values: List[Tuple[str, Any]], args: list, defaults: list
        ) -> None:
            for keyword, value in keyword_values:
                if _should_include_arg(keyword, value, [arg.arg for arg in args]):
                    args.append(ast.arg(arg=keyword, annotation=None))
                    global_keyword_name = f"{keyword}"
                    saved_defaults[global_keyword_name] = value
                    defaults.append(ast.Name(id=global_keyword_name, ctx=ast.Load()))

        # get the defaulted arguments and keyword only arguments
        if self.has_pre_controller:
            add_non_conflicting_parameters(
                self.pre_controller.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.pre_controller.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        if self.has_filter:
            add_non_conflicting_parameters(
                self.filter.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.filter.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        if self.has_sort_key:
            add_non_conflicting_parameters(
                self.sort_key.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.sort_key.get_keyword_only_args(),
                kwonlyargs,
                kw_defaults,
            )

        if self.has_sort_cmp:
            add_non_conflicting_parameters(
                self.sort_cmp.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.sort_cmp.get_keyword_only_args(),
                kwonlyargs,
                kw_defaults,
            )

        if self.has_action:
            add_non_conflicting_parameters(
                self.action.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.action.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        if self.has_fold:
            add_non_conflicting_parameters(
                self.fold.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.fold.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        if self.has_post_controller:
            add_non_conflicting_parameters(
                self.post_controller.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.post_controller.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        # check for arg unpacks
        arg_unpack_name = None
        if self.has_pre_controller:
            arg_unpack_name = self.pre_controller.varargs
        if self.has_filter:
            if arg_unpack_name is None:
                arg_unpack_name = self.filter.varargs
            elif self.filter.has_arg_unpack and self.filter.varargs != arg_unpack_name:
                raise ArgumentError(
                    dedent(
                        f'{FILTER_METHOD_NAME} controlled action uses "{self.filter.varargs}" as the argument unpack variable name, \
                    but it was previously defined as "{arg_unpack_name}". \
                    The argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_sort_key:
            if arg_unpack_name is None:
                arg_unpack_name = self.sort_key.varargs
            elif (
                self.sort_key.has_arg_unpack
                and self.sort_key.varargs != arg_unpack_name
            ):
                raise ArgumentError(
                    dedent(
                        f'{SORT_KEY_METHOD_NAME} controlled action uses "{self.sort_key.varargs}" as the argument unpack variable name, \
                    but it was previously defined as "{arg_unpack_name}". \
                    The argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_sort_cmp:
            if arg_unpack_name is None:
                arg_unpack_name = self.sort_cmp.varargs
            elif (
                self.sort_cmp.has_arg_unpack
                and self.sort_cmp.varargs != arg_unpack_name
            ):
                raise ArgumentError(
                    dedent(
                        f'{SORT_CMP_METHOD_NAME} controlled action uses "{self.sort_cmp.varargs}" as the argument unpack variable name, \
                    but it was previously defined as "{arg_unpack_name}". \
                    The argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_action:
            if arg_unpack_name is None:
                arg_unpack_name = self.action.varargs
            elif self.action.has_arg_unpack and self.action.varargs != arg_unpack_name:
                raise ArgumentError(
                    dedent(
                        f'{ACTION_METHOD_NAME} controlled action uses "{self.action.varargs}" as the argument unpack variable name, \
                    but it was previously defined as "{arg_unpack_name}". \
                    The argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_fold:
            if arg_unpack_name is None:
                arg_unpack_name = self.fold.varargs
            elif self.fold.has_arg_unpack and self.fold.varargs != arg_unpack_name:
                raise ArgumentError(
                    dedent(
                        f'{FOLD_METHOD_NAME} controlled action uses "{self.fold.varargs}" as the argument unpack variable name, \
                    but it was previously defined as "{arg_unpack_name}". \
                    The argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_post_controller:
            if arg_unpack_name is None:
                arg_unpack_name = self.post_controller.varargs
            elif (
                self.post_controller.has_arg_unpack
                and self.post_controller.varargs != arg_unpack_name
            ):
                raise ArgumentError(
                    dedent(
                        f'{POST_CONTROLLER_METHOD_NAME} controlled action uses "{self.post_controller.varargs}" as the argument unpack variable name, \
                    but it was previously defined as "{arg_unpack_name}". \
                    The argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )

        if arg_unpack_name is not None:
            var_arg = ast.arg(arg=arg_unpack_name, annotation=None)

        # check for kwarg unpacks
        kwarg_name = None
        if self.has_pre_controller:
            kwarg_name = self.pre_controller.varkw
        if self.has_filter:
            if kwarg_name is None:
                kwarg_name = self.filter.varkw
            elif self.filter.has_kwarg_unpack and self.filter.varkw != kwarg_name:
                raise ArgumentError(
                    dedent(
                        f'{FILTER_METHOD_NAME} controlled action uses "{self.filter.varkw}" as the keyword argument unpack variable name, \
                    but it was previously defined as "{kwarg_name}". \
                    The keyword argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_sort_key:
            if kwarg_name is None:
                kwarg_name = self.sort_key.varkw
            elif self.sort_key.has_kwarg_unpack and self.sort_key.varkw != kwarg_name:
                raise ArgumentError(
                    dedent(
                        f'{SORT_KEY_METHOD_NAME} controlled action uses "{self.sort_key.varkw}" as the keyword argument unpack variable name, \
                    but it was previously defined as "{kwarg_name}". \
                    The keyword argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_sort_cmp:
            if kwarg_name is None:
                kwarg_name = self.sort_cmp.varkw
            elif self.sort_cmp.has_kwarg_unpack and self.sort_cmp.varkw != kwarg_name:
                raise ArgumentError(
                    dedent(
                        f'{SORT_CMP_METHOD_NAME} controlled action uses "{self.sort_cmp.varkw}" as the keyword argument unpack variable name, \
                    but it was previously defined as "{kwarg_name}". \
                    The keyword argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_action:
            if kwarg_name is None:
                kwarg_name = self.action.varkw
            elif self.action.has_kwarg_unpack and self.action.varkw != kwarg_name:
                raise ArgumentError(
                    dedent(
                        f'{ACTION_METHOD_NAME} controlled action uses "{self.action.varkw}" as the keyword argument unpack variable name, \
                    but it was previously defined as "{kwarg_name}". \
                    The keyword argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_fold:
            if kwarg_name is None:
                kwarg_name = self.fold.varkw
            elif self.fold.has_kwarg_unpack and self.fold.varkw != kwarg_name:
                raise ArgumentError(
                    dedent(
                        f'{FOLD_METHOD_NAME} controlled action uses "{self.fold.varkw}" as the keyword argument unpack variable name, \
                    but it was previously defined as "{kwarg_name}". \
                    The keyword argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )
        if self.has_post_controller:
            if kwarg_name is None:
                kwarg_name = self.post_controller.varkw
            elif (
                self.post_controller.has_kwarg_unpack
                and self.post_controller.varkw != kwarg_name
            ):
                raise ArgumentError(
                    dedent(
                        f'{POST_CONTROLLER_METHOD_NAME} controlled action uses "{self.post_controller.varkw}" as the keyword argument unpack variable name, \
                    but it was previously defined as "{kwarg_name}". \
                    The keyword argument unpack variable must be the same name across all controlled methods that use it.'
                    )
                )

        if kwarg_name is not None:
            kwarg = ast.arg(arg=kwarg_name, annotation=None)

        # create the signatures arguments
        func_args = ast.arguments(
            posonlyargs=posonlyargs,
            args=args,
            vararg=var_arg,
            kwonlyargs=kwonlyargs,
            kw_defaults=kw_defaults,
            kwarg=kwarg,
            defaults=defaults,
        )
        return func_args, saved_defaults
