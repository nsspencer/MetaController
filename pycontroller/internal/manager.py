import ast
from functools import cmp_to_key
from heapq import nlargest as _heapq_nlargest
from heapq import nsmallest as _heapq_nsmallest
from itertools import islice as _itertools_islice
from typing import Any, Callable, Dict, List, Tuple

from pycontroller.internal.controlled_methods import Action, Filter, Preference
from pycontroller.internal.namespace import *
from pycontroller.internal.utils import generate_positional_args


class ControllerManager:

    def __init__(self, cls, name: str, attrs: dict, previous_frame) -> None:
        self.controller = cls
        self.name = name
        self.attrs = attrs
        self.generated_call_fn = None
        self.saved_global_kwargs = {}
        self.max_chosen_handled = False

        # Get local and global variables from the previous frame
        self.previous_frame = previous_frame

        controlled_methods = {
            k: v for k, v in attrs.items() if callable(v) and k in CONTROLLED_METHODS
        }

        self.action = (
            Action(controlled_methods[ACTION_FN_NAME], is_debug=cls.debug_mode)
            if controlled_methods.get(ACTION_FN_NAME, None) is not None
            else None
        )

        self.filter = (
            Filter(controlled_methods[FILTER_FN_NAME], is_debug=cls.debug_mode)
            if controlled_methods.get(FILTER_FN_NAME, None) is not None
            else None
        )

        # make sure there is only one preference (preference or preference_cmp) defined
        if (
            PREFERENCE_CMP_FN_NAME in controlled_methods
            and PREFERENCE_FN_NAME in controlled_methods
        ):
            raise AttributeError(
                'Cannot define both a "preference" and "preference_cmp" in the same controller. \
                    "preference" is usually more performant than "preference_cmp"'
            )

        if PREFERENCE_FN_NAME in controlled_methods:
            self.preference = Preference(
                controlled_methods[PREFERENCE_FN_NAME],
                cls.simple_sort,
                cls.reverse_sort,
                is_comparator=False,
                is_debug=cls.debug_mode,
            )
        elif PREFERENCE_CMP_FN_NAME in controlled_methods:
            self.preference = Preference(
                controlled_methods[PREFERENCE_CMP_FN_NAME],
                cls.simple_sort,
                cls.reverse_sort,
                is_comparator=True,
                is_debug=cls.debug_mode,
            )
        else:
            self.preference = None

        self.validate_class_attributes()
        self.validate_class_methods()
        self.assign_call_method(self.generate_call_method())

    def validate_class_attributes(self):
        self.controller.simple_sort = bool(self.controller.simple_sort)
        if self.controller.simple_sort:
            if self.has_preference:
                raise ValueError(
                    'Cannot use "simple_sort" and define a "preference" or "preference_cmp" at the same time.'
                )

        self.controller.reverse_sort = bool(self.controller.reverse_sort)
        if self.controller.reverse_sort:
            if not self.has_preference and not self.controller.simple_sort:
                raise ValueError(
                    'Cannot use "reverse_sort" without a "preference" or "simple_sort" defined.'
                )
        if (
            self.controller.fixed_max_chosen is not None
            and self.controller.dynamic_max_chosen is True
        ):
            raise ValueError(
                'Cannot set "fixed_max_chosen" value and also use "dynamic_max_chosen".'
            )

    def validate_class_methods(self):
        if self.has_action:
            if self.action.get_min_required_call_args() > len(
                self.action.signature.full_call_arg_spec.args
            ):
                raise AttributeError(
                    f"Action signature requires at least {self.action.get_min_required_call_args()} positional parameter(s)."
                )
        if self.has_filter:
            if self.filter.get_min_required_call_args() > len(
                self.filter.signature.full_call_arg_spec.args
            ):
                raise AttributeError(
                    f"Filter signature requires at least {self.filter.get_min_required_call_args()} positional parameter(s)."
                )

        if self.has_preference:
            if self.preference.get_min_required_call_args() > len(
                self.preference.signature.full_call_arg_spec.args
            ):
                raise AttributeError(
                    f"Preference signature requires at least {self.preference.get_min_required_call_args()} positional parameter(s)."
                )

    def get_call_signature_args(self) -> ast.arguments:
        """
        The goal of this function is to determine the set of parameters that make up the call method
        of this controller. This is done by inspecting the paramters of the controlled methods
        that are a part of this controller.

        Position only and non-defaulted keyword arguments are converted to placeholder argument
        values, like: arg0, arg1, arg2, etc..

        Keyword only and default arguments are allowed to shared the same name, but they must also
        share the same default argument. Duplicated keywords with different default values
        are invalid, and an error will be thrown.

        Variable args are supported, and will be transformed to a placeholder name like: *args

        Kwargs are supported, and will be transformed to a placeholder name like: **kwargs

        Raises:
            AttributeError: for duplicate keyword/default IDs without the same default value.

        Returns:
            ast.arguments: Arguments for the generated call method.
        """
        # arguments to be used when constructing the resulting ast.arguments
        posonlyargs = []
        args = []
        kwonlyargs = []
        kw_defaults = []
        defaults = []
        var_arg = None
        kwarg = None

        # add the class argument
        posonlyargs.append(
            ast.arg(arg=CLASS_ARG_NAME, annotation=None, type_comment=None)
        )

        # add the dynamic_max_chosen K argument
        if self.controller.dynamic_max_chosen:
            posonlyargs.append(
                ast.arg(arg=MAX_CHOSEN_ARG_NAME, annotation=None, type_comment=None)
            )

        # add the partition argument
        posonlyargs.append(
            ast.arg(arg=PARTITION_NAME, annotation=None, type_comment=None)
        )

        # determine how many position only placeholders to generate
        pos_only_placeholder_count = 0
        if self.has_action:
            num_args = len(self.action.signature.args) - len(
                self.action.signature.defaults
            )
            if not self.action.signature.is_staticmethod:
                num_args -= 1  # remove one for the class argument
            num_args -= self.action.get_min_required_call_args()
            pos_only_placeholder_count = max(num_args, pos_only_placeholder_count)

        if self.has_filter:
            num_args = len(self.filter.signature.args) - len(
                self.filter.signature.defaults
            )
            if not self.filter.signature.is_staticmethod:
                num_args -= 1  # remove one for the class argument
            num_args -= self.filter.get_min_required_call_args()
            pos_only_placeholder_count = max(num_args, pos_only_placeholder_count)

        if self.has_preference:
            num_args = len(self.preference.signature.args) - len(
                self.preference.signature.defaults
            )
            if not self.preference.signature.is_staticmethod:
                num_args -= 1  # remove one for the class argument
            num_args -= self.preference.get_min_required_call_args()
            pos_only_placeholder_count = max(num_args, pos_only_placeholder_count)

        # generate the position only args that take the place of the args from the
        # controlled methods
        posonlyargs.extend(generate_positional_args(pos_only_placeholder_count))

        # defined as an inner function to pass args and saved_global_kwargs into the namespace
        def _should_include_arg(
            keyword: str,
            default: Any,
            existing_args: List[str],
            saved_global_kwargs: Dict[str, Any] = self.saved_global_kwargs,
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
                _ctrl_keyword_name = f"{MANGLED_KWARG_NAME}{keyword}"
                if _ctrl_keyword_name in saved_global_kwargs:
                    val = saved_global_kwargs[_ctrl_keyword_name]
                if default == val:
                    return False
                else:
                    raise AttributeError(
                        f'Duplicate keyword argument "{keyword}" with different default values.\
                            Shared keyword arguments must have the same default value.\
                                Equality is checked with the __eq__ operator.'
                    )
            return True

        def add_non_conflicting_parameters(
            keyword_values: List[Tuple[str, Any]], args: list, defaults: list
        ) -> None:
            for keyword, value in keyword_values:
                if _should_include_arg(keyword, value, args):
                    args.append(ast.arg(arg=keyword, annotation=None))
                    global_keyword_name = f"{MANGLED_KWARG_NAME}{keyword}"
                    self.saved_global_kwargs[global_keyword_name] = value
                    defaults.append(ast.Name(id=global_keyword_name, ctx=ast.Load()))

        # get the defaulted arguments
        if self.has_action:
            add_non_conflicting_parameters(
                self.action.signature.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.action.signature.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        if self.has_filter:
            add_non_conflicting_parameters(
                self.filter.signature.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.filter.signature.get_keyword_only_args(), kwonlyargs, kw_defaults
            )

        if self.has_preference:
            add_non_conflicting_parameters(
                self.preference.signature.get_defaulted_args(), args, defaults
            )
            add_non_conflicting_parameters(
                self.preference.signature.get_keyword_only_args(),
                kwonlyargs,
                kw_defaults,
            )

        # check for arg unpacks
        has_var_arg = False
        if self.has_action:
            has_var_arg = self.action.signature.has_arg_unpack or has_var_arg
        if self.has_filter:
            has_var_arg = self.filter.signature.has_arg_unpack or has_var_arg
        if self.has_preference:
            has_var_arg = self.preference.signature.has_arg_unpack or has_var_arg
        if has_var_arg:
            var_arg = ast.arg(arg=VAR_ARG_NAME, annotation=None)

        # check for kwarg unpacks
        has_kwarg = False
        if self.has_action:
            has_kwarg = self.action.signature.has_kwarg_unpack or has_kwarg
        if self.has_filter:
            has_kwarg = self.filter.signature.has_kwarg_unpack or has_kwarg
        if self.has_preference:
            has_kwarg = self.preference.signature.has_kwarg_unpack or has_kwarg
        if has_kwarg:
            kwarg = ast.arg(arg=KWARG_NAME, annotation=None)

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
        return func_args

    def generate_call_method(self) -> Callable:
        get_elements = ast.Name(id=PARTITION_NAME, ctx=ast.Load())
        setup_statements = []

        max_chosen_element = None
        if self.controller.fixed_max_chosen:
            max_chosen_element = ast.Constant(
                value=self.controller.fixed_max_chosen, kind=int
            )
        elif self.controller.dynamic_max_chosen:
            max_chosen_element = ast.Name(id=MAX_CHOSEN_ARG_NAME, ctx=ast.Load())

        if self.has_filter:
            if not self.has_preference:
                _max_chosen = max_chosen_element
            else:
                _max_chosen = None
            get_elements, _setup_statements = self.filter.generate_expression(
                get_elements, _max_chosen
            )
            setup_statements.extend(_setup_statements)
            _max_chosen = None

        if self.has_preference:
            get_elements, _setup_stmt = self.preference.generate_expression(
                get_elements, max_chosen_element
            )
            setup_statements.extend(_setup_stmt)
            max_chosen_element = None

        elif self.controller.simple_sort == True:
            ###
            # special case for defining preference without a preference function,
            # using the built in comparison dunder methods of the objects in
            # the partition.
            #
            keywords = []
            if self.controller.reverse_sort == True:
                keywords.append(ast.keyword(arg="reverse", value=ast.Constant(True)))

            # Create the function call node
            get_elements = ast.Call(
                func=ast.Name(id="sorted", ctx=ast.Load()),
                args=[get_elements],
                keywords=keywords,
            )

        if self.has_action:
            get_elements, _setup_stmt = self.action.generate_expression(
                get_elements, max_chosen_element
            )
            setup_statements.extend(_setup_stmt)
            max_chosen_element = None

        if max_chosen_element:
            get_elements = ast.Call(
                func=ast.Name(id="_itertools_islice", ctx=ast.Load()),
                args=[get_elements, max_chosen_element],
                keywords=[],
            )

        generator_expr = get_elements
        if self.has_action or self.has_filter or max_chosen_element is not None:
            generator_expr = ast.Call(
                func=ast.Name(id="list", ctx=ast.Load()),
                args=[generator_expr],
                keywords=[],
            )

        return_statement = ast.Return(generator_expr)
        body_code = setup_statements + [return_statement]
        signature_args = self.get_call_signature_args()
        call_fn = ast.FunctionDef(
            name=GENERATED_FUNCTION_NAME,
            args=signature_args,
            body=[body_code],
            decorator_list=[],
            returns=None,
            lineno=0,
            col_offset=0,
        )

        self.generated_call_fn = ast.unparse(call_fn)

        _globals = self.previous_frame.f_globals
        _globals.update(self.previous_frame.f_locals)
        _globals.update(
            {
                "_heapq_nsmallest": _heapq_nsmallest,
                "_cmp_to_key": cmp_to_key,
                "_heapq_nlargest": _heapq_nlargest,
                "_itertools_islice": _itertools_islice,
            }
        )
        _globals.update(self.saved_global_kwargs)
        _locals = {}
        eval(
            compile(self.generated_call_fn, filename="<ast>", mode="exec"),
            _globals,
            _locals,
        )
        return _locals[GENERATED_FUNCTION_NAME]

    def assign_call_method(self, call_fn: Callable) -> None:
        self.controller.__call__ = call_fn

    @property
    def has_action(self) -> bool:
        return self.action is not None

    @property
    def has_filter(self) -> bool:
        return self.filter is not None

    @property
    def has_preference(self) -> bool:
        return self.preference is not None
