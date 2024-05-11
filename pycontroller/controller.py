import ast
import inspect
import warnings
from enum import Enum
from functools import cmp_to_key
from heapq import nlargest, nsmallest
from textwrap import dedent
from typing import Callable, List

PARTITION_NAME = "partition"
CHOSEN_NAME = "chosen"
ABBREVIATED_FILTER_FN = "filter_fn"
ABBREVIATED_PREFERENCE_FN = "preference_fn"
ABBREVIATED_ACTION_FN = "action_fn"
CALL_METHOD_NAME = "call"
DYNAMIC_MAX_CHOSEN_NAME = "n"

PREFERENCE_FN_ARG0 = "a"
PREFERENCE_FN_ARG1 = "b"

ARG_UNPACK = "*args"
KWARG_UNPACK = "**kwargs"

ACTION_FN_NAME = "action"
FILTER_FN_NAME = "filter"
PREFERENCE_FN_NAME = "preference"
CONTROLLED_METHODS = [ACTION_FN_NAME, FILTER_FN_NAME, PREFERENCE_FN_NAME]


class SignatureHelper:
    def __init__(self, fn: Callable) -> None:
        if hasattr(fn, "__wrapped__"):
            self.spec = inspect.getfullargspec(fn.__wrapped__)
            self.is_wrapped = True
        else:
            self.spec = inspect.getfullargspec(fn)
            self.is_wrapped = False
        self.has_explicit_return = SignatureHelper.fn_has_explicit_return(fn)
        self.fn = fn

    @staticmethod
    def fn_has_explicit_return(f) -> bool:
        try:
            source = dedent(inspect.getsource(f))
            module = ast.parse(source)
            function_def = module.body[0]  # Get the function definition from the module
            has_return = any(isinstance(node, ast.Return) for node in function_def.body)
        except BaseException:
            warnings.warn(
                f'Unable to determine if "{f.__name__}" has an explicit return. Assuming it does.'
            )
            has_return = True  # assume it returns
        return has_return

    @property
    def is_staticmethod(self) -> bool:
        return isinstance(self.fn, staticmethod)

    @property
    def positional_args(self) -> list:
        if self.spec[0] is None:
            return []
        if len(self.keyword_arguments) != 0:
            return self.spec.args[: -len(self.keyword_arguments)]
        return self.spec.args

    @property
    def keyword_arguments(self) -> list:
        if self.spec[3] is None:
            return []
        names = self.spec.args[len(self.spec.args[: -len(self.spec[3])]) :]
        kwargs = list(zip(names, self.spec[3]))
        return kwargs

    @property
    def has_positional_args(self) -> bool:
        return len(self.positional_args) != 0

    @property
    def has_keyword_args(self) -> bool:
        return len(self.keyword_arguments) != 0

    @property
    def has_arg_unpack(self):
        return self.spec[1] is not None

    @property
    def has_kwarg_unpack(self):
        return self.spec[2] is not None

    @property
    def all_args(self) -> list:
        if self.spec.args is None:
            return []
        return self.spec.args

    @property
    def non_class_positional_args(self) -> list:
        if self.is_staticmethod:
            return self.positional_args
        return self.positional_args[1:]

    @property
    def full_call_arg_spec(self) -> inspect.FullArgSpec:
        if self.is_staticmethod:
            return self.spec
        # remove the self argument
        return inspect.FullArgSpec(
            args=self.spec.args[1:],
            varargs=self.spec.varargs,
            varkw=self.spec.varkw,
            defaults=self.spec.defaults,
            kwonlyargs=self.spec.kwonlyargs,
            kwonlydefaults=self.spec.kwonlydefaults,
            annotations=self.spec.annotations,
        )


class ReturnType(Enum):
    NONE = 0
    VALUE = 1
    GENERATOR = 2


class ControllerSpec:
    def __init__(self, cls: "MetaController", name: str, attrs: dict) -> None:
        self.cls = cls
        self.name = name
        self.attrs = attrs
        self.controlled_methods = {
            k: SignatureHelper(v)
            for k, v in attrs.items()
            if callable(v) and k in CONTROLLED_METHODS
        }
        pass

    @property
    def expected_return_type(self) -> ReturnType:
        if self.cls.return_generator:
            return ReturnType.GENERATOR

        if self.has_action:
            if self.controlled_methods[ACTION_FN_NAME].has_explicit_return:
                return ReturnType.VALUE
            return ReturnType.NONE
        return ReturnType.VALUE

    # Action properties

    @property
    def has_action(self) -> bool:
        return ACTION_FN_NAME in self.controlled_methods

    @property
    def action_num_required_args(self) -> int:
        if not self.has_action:
            return 0

        required_length = 2
        if self.cls.no_partition:
            required_length -= 1
        if self.controlled_methods[ACTION_FN_NAME].is_staticmethod:
            required_length -= 1
        return required_length

    @property
    def action_call_args(self) -> List[str]:
        if not self.has_action:
            return list()
        fn = self.controlled_methods[ACTION_FN_NAME]
        return ControllerSpec.get_fn_call_arg_list(fn)

    # Filter properties
    @property
    def has_filter(self) -> bool:
        return FILTER_FN_NAME in self.controlled_methods

    @property
    def filter_num_required_args(self) -> int:
        if not self.has_filter:
            return 0

        required_length = 2
        if self.controlled_methods[FILTER_FN_NAME].is_staticmethod:
            required_length -= 1
        return required_length

    @property
    def filter_call_args(self) -> List[str]:
        if not self.has_filter:
            return list()
        fn = self.controlled_methods[FILTER_FN_NAME]
        return ControllerSpec.get_fn_call_arg_list(fn)

    # Preference properties
    @property
    def has_preference(self) -> bool:
        return PREFERENCE_FN_NAME in self.controlled_methods

    @property
    def preference_num_required_args(self) -> int:
        if not self.has_preference:
            return 0

        required_length = 3
        if self.controlled_methods[PREFERENCE_FN_NAME].is_staticmethod:
            required_length -= 1
        return required_length

    @property
    def preference_call_args(self) -> List[str]:
        if not self.has_preference:
            return list()
        fn = self.controlled_methods[PREFERENCE_FN_NAME]
        return ControllerSpec.get_fn_call_arg_list(fn)

    # Signature properties
    @property
    def signature_args(self) -> List[str]:
        signature_args = ["self"]
        if self.cls.use_dynamic_max_chosen:
            signature_args.append(DYNAMIC_MAX_CHOSEN_NAME)
        if self.cls.no_partition == False:
            signature_args.append(PARTITION_NAME)

        # add positional arguments
        num_positional_args = 0
        if self.has_action:
            num_positional_args = max(
                len(self.controlled_methods[ACTION_FN_NAME].non_class_positional_args)
                - self.action_num_required_args,
                num_positional_args,
            )

        if self.has_filter:
            num_positional_args = max(
                len(self.controlled_methods[FILTER_FN_NAME].non_class_positional_args)
                - self.action_num_required_args,
                num_positional_args,
            )

        if self.has_preference:
            num_positional_args = max(
                len(
                    self.controlled_methods[
                        PREFERENCE_FN_NAME
                    ].non_class_positional_args
                )
                - self.action_num_required_args,
                num_positional_args,
            )
        signature_args.extend(
            ControllerSpec.generate_positional_arg_names(num_positional_args)
        )

        # check for arg unpacks and kwarg unpacks
        arg_unpack = False
        kwarg_unpack = False
        if self.has_action:
            if self.controlled_methods[ACTION_FN_NAME].has_arg_unpack:
                arg_unpack = True
            if self.controlled_methods[ACTION_FN_NAME].has_kwarg_unpack:
                kwarg_unpack = True
        if self.has_filter:
            if self.controlled_methods[FILTER_FN_NAME].has_arg_unpack:
                arg_unpack = True
            if self.controlled_methods[FILTER_FN_NAME].has_kwarg_unpack:
                kwarg_unpack = True
        if self.has_preference:
            if self.controlled_methods[PREFERENCE_FN_NAME].has_arg_unpack:
                arg_unpack = True
            if self.controlled_methods[PREFERENCE_FN_NAME].has_kwarg_unpack:
                kwarg_unpack = True

        # add arg unpacks
        if arg_unpack:
            signature_args.append(ARG_UNPACK)

        # add keyword arguments
        keyword_args = []
        if self.has_action:
            keyword_args.extend(
                self.controlled_methods[ACTION_FN_NAME].keyword_arguments
            )
        if self.has_filter:
            keyword_args.extend(
                self.controlled_methods[FILTER_FN_NAME].keyword_arguments
            )
        if self.has_preference:
            keyword_args.extend(
                self.controlled_methods[PREFERENCE_FN_NAME].keyword_arguments
            )
        cleaned_kwargs = []
        seen_kwargs = set()
        for kwarg in keyword_args:
            if kwarg[0] in seen_kwargs:
                continue
            cleaned_kwargs.append(kwarg)
            seen_kwargs.add(kwarg[0])
        signature_args.extend(cleaned_kwargs)

        # add kwarg unpacks
        if kwarg_unpack:
            signature_args.append(KWARG_UNPACK)

        return signature_args

    @staticmethod
    def generate_positional_arg_names(num_args: int, prefix: str = "arg") -> List[str]:
        return [prefix + str(i) for i in range(num_args)]

    @staticmethod
    def get_fn_call_arg_list(fn: SignatureHelper) -> list:
        args = fn.non_class_positional_args

        if fn.has_arg_unpack:
            args.append(ARG_UNPACK)

        args.extend(fn.keyword_arguments)

        if fn.has_kwarg_unpack:
            args.append(KWARG_UNPACK)
        return args


class MetaController(type):
    name = None
    no_partition = False
    return_generator = False
    max_chosen = None
    use_dynamic_max_chosen = False
    use_simple_sort = False
    reverse_sort = False
    static_mode = False
    include_globals = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name == "Controller":
            return

        cls.name: str = cls.name or name
        cls.spec = ControllerSpec(cls, name, attrs)
        cls._generated_call: str = ""
        cls._has_action: bool = False
        cls._has_filter: bool = False
        cls._has_preference: bool = False

        if "action" in attrs:
            cls._has_action = True
            cls._action_arg_spec = SignatureHelper(attrs["action"])
            required_length = 2
            if cls.no_partition:
                required_length -= 1
            if cls._action_arg_spec.is_staticmethod:
                required_length -= 1
            cls._action_required_arg_length = required_length

        if "filter" in attrs:
            cls._has_filter = True
            cls._filter_arg_spec = SignatureHelper(attrs["filter"])
            required_length = 2
            if cls._filter_arg_spec.is_staticmethod:
                required_length -= 1
            cls._filter_required_arg_length = required_length

        if "preference" in attrs:
            cls._has_preference = True
            cls._preference_arg_spec = SignatureHelper(attrs["preference"])
            required_length = 3
            if cls._preference_arg_spec.is_staticmethod:
                required_length -= 1
            cls._preference_required_arg_length = required_length

        MetaController.validate_attributes(cls, attrs)
        MetaController.validate_methods(cls, attrs)
        call_fn = MetaController.generate_call_method(cls)
        if cls.static_mode:
            cls.__new__ = call_fn
            cls.__init__ = call_fn
        else:
            cls.__call__ = call_fn

    @staticmethod
    def validate_attributes(cls: "MetaController", attrs: dict) -> None:
        if cls.no_partition:
            if cls.max_chosen is not None:
                raise AttributeError(
                    'Cannot have "no_partition" and "max_chosen" defined together.'
                )
            if cls.use_dynamic_max_chosen:
                raise AttributeError(
                    'Cannot have "no_partition" and "use_dynamic_max_chosen" defined together.'
                )
            if cls.return_generator:
                raise AttributeError(
                    'Cannot have "no_partition" and "return_generator" defined together.'
                )
            if cls.use_simple_sort:
                raise AttributeError(
                    'Cannot have "no_partition" and "use_simple_sort" defined together.'
                )
            if cls.reverse_sort:
                raise AttributeError(
                    'Cannot have "no_partition" and "reverse_sort" defined together.'
                )

        if not isinstance(cls.include_globals, dict):
            raise AttributeError('"include_globals" must be a dictionary.')

        if cls.max_chosen is not None:
            if not isinstance(cls.max_chosen, int) or cls.max_chosen <= 0:
                raise AttributeError('"max_chosen" must be a positive integer.')

        if cls.reverse_sort and not cls._has_preference:
            raise AttributeError(
                'Cannot have "reverse_sort" without a preference defined.'
            )

    @staticmethod
    def validate_methods(cls: "MetaController", attrs: dict) -> None:
        # make sure there is some action that was created
        if (
            "action" not in attrs
            and "filter" not in attrs
            and "preference" not in attrs
        ):
            raise TypeError(
                "Invalid controller definition. You must define at least an action, filter, or preference."
            )

        if "action" in attrs:
            if (
                len(cls._action_arg_spec.positional_args)
                < cls._action_required_arg_length
            ):
                if cls._action_required_arg_length == 2:
                    raise TypeError(
                        '"action" requires a minimum of 2 arguments: "self" and "chosen".'
                    )

                elif cls.no_partition:
                    raise TypeError(
                        '"action" requires a minimum of 1 argument: "chosen".'
                    )

                else:
                    raise TypeError('"action" requires a minimum of 1 argument.')

        if "filter" in attrs:
            if cls.no_partition:
                raise TypeError('"filter" not supported in "no_partition" mode.')

            if not cls._filter_arg_spec.has_explicit_return:
                raise ValueError("filter requires a boolean return value.")

            if (
                len(cls._filter_arg_spec.positional_args)
                < cls._filter_required_arg_length
            ):
                if cls._filter_required_arg_length == 2:
                    raise TypeError(
                        '"filter" requires a minimum of 2 arguments: "self" and "chosen".'
                    )

                else:
                    raise TypeError(
                        '"filter" requires a minimum of 1 arguments: "chosen".'
                    )

        if "preference" in attrs:
            if cls.no_partition:
                raise TypeError('"preference" not supported in "no_partition" mode.')

            if not cls._preference_arg_spec.has_explicit_return:
                raise ValueError("preference requires a boolean return value.")

            if (
                len(cls._preference_arg_spec.positional_args)
                < cls._preference_required_arg_length
            ):
                if cls._preference_required_arg_length == 3:
                    raise TypeError(
                        '"preference" requires a minimum of 3 arguments: "self", "a", and "b".'
                    )

                else:
                    raise TypeError(
                        '"preference" requires a minimum of 2 arguments: "a", and "b".'
                    )

    @staticmethod
    def generate_call_method(cls: "MetaController"):

        if cls._has_preference:
            preference = MetaController.generate_preference(cls)
            filter = MetaController.generate_filter(cls)
            action = MetaController.generate_action(cls)

        if cls._action_arg_spec.has_explicit_return:
            pass

    def generate_preference(cls: "MetaController"):
        pass

    def generate_filter(cls: "MetaController"):
        pass

    def generate_action(cls: "MetaController"):
        pass

    @staticmethod
    def generate_call_method_original(cls: "MetaController") -> Callable:

        signature_args = ["self"]
        if cls.no_partition == False:
            signature_args.append(PARTITION_NAME)

        if cls.use_dynamic_max_chosen:
            signature_args.append(DYNAMIC_MAX_CHOSEN_NAME)

        # TODO: do something smarter with positional arguments since unpacking is slow
        needs_args = False
        if cls._has_action:
            if (
                len(cls._action_arg_spec.positional_args)
                != cls._action_required_arg_length
            ) or (cls._action_arg_spec.has_arg_unpack):
                needs_args = True

        if cls._has_filter:
            if (
                len(cls._filter_arg_spec.positional_args)
                != cls._filter_required_arg_length
            ) or (cls._filter_arg_spec.has_arg_unpack):
                needs_args = True

        if cls._has_preference:
            if (
                len(cls._preference_arg_spec.positional_args)
                != cls._preference_required_arg_length
            ) or (cls._preference_arg_spec.has_arg_unpack):
                needs_args = True

        if needs_args:
            signature_args.append("*args")

        # TODO: do something smarter with named keyword arguments since unpacking is slow
        needs_kwargs = False
        if cls._has_action:
            if (cls._action_arg_spec.has_keyword_args) or (
                cls._action_arg_spec.has_kwarg_unpack
            ):
                needs_kwargs = True

        if cls._has_filter:
            if (
                cls._filter_arg_spec.has_keyword_args
                or cls._filter_arg_spec.has_kwarg_unpack
            ):
                needs_kwargs = True

        if cls._has_preference:
            if (
                cls._preference_arg_spec.has_keyword_args
                or cls._preference_arg_spec.has_kwarg_unpack
            ):
                needs_kwargs = True

        if needs_kwargs:
            signature_args.append("**kwargs")

        generated_call_str = ""
        signature_str = f"def {CALL_METHOD_NAME}({', '.join(signature_args)}):"

        # check for the speedy happy path
        setup_statements = []
        if needs_args == False and needs_kwargs == False:

            max_chosen_handled = False
            get_elements_str = PARTITION_NAME
            if cls._has_filter:
                setup_statements.append(f"{ABBREVIATED_FILTER_FN} = self.filter")
                get_elements_str = (
                    f"filter({ABBREVIATED_FILTER_FN}, " + get_elements_str + ")"
                )

            if cls._has_preference:
                setup_statements.append(
                    f"{ABBREVIATED_PREFERENCE_FN} = self.preference"
                )
                if cls.max_chosen is None:
                    if cls.reverse_sort:
                        get_elements_str = f"sorted({get_elements_str}, key=cmp_to_key({ABBREVIATED_PREFERENCE_FN}), reverse=True)"
                    else:
                        get_elements_str = f"sorted({get_elements_str}, key=cmp_to_key({ABBREVIATED_PREFERENCE_FN}))"

                else:
                    max_chosen_handled = True
                    if cls.reverse_sort:
                        get_elements_str = f"nlargest({cls.max_chosen}, {get_elements_str}, key=cmp_to_key({ABBREVIATED_PREFERENCE_FN}))"
                    else:
                        get_elements_str = f"nsmallest({cls.max_chosen}, {get_elements_str}, key=cmp_to_key({ABBREVIATED_PREFERENCE_FN}))"

            if max_chosen_handled == False:
                if cls.max_chosen:
                    if cls._has_filter:
                        get_elements_str = "list(" + get_elements_str + ")"
                    else:
                        get_elements_str = get_elements_str + f"[:{cls.max_chosen}]"
                    max_chosen_handled = True

            return_statement_str = ""
            if cls._has_action:
                setup_statements.append(f"{ABBREVIATED_ACTION_FN} = self.action")
                if cls._action_arg_spec.has_explicit_return:
                    return_statement_str = "return "
                    if cls.return_generator:
                        return_statement_str = (
                            return_statement_str
                            + f"({ABBREVIATED_ACTION_FN}({CHOSEN_NAME}) for {CHOSEN_NAME} in {get_elements_str})"
                        )
                    else:
                        return_statement_str = (
                            return_statement_str
                            + f"[{ABBREVIATED_ACTION_FN}({CHOSEN_NAME}) for {CHOSEN_NAME} in {get_elements_str}]"
                        )
                else:
                    if cls.return_generator:
                        return_statement_str = (
                            return_statement_str
                            + f"return ({ABBREVIATED_ACTION_FN}({CHOSEN_NAME}) for {CHOSEN_NAME} in {get_elements_str})"
                        )
                    else:
                        return_statement_str = (
                            return_statement_str
                            + f"[{ABBREVIATED_ACTION_FN}({CHOSEN_NAME}) for {CHOSEN_NAME} in {get_elements_str}]"
                        )

            # no action
            else:
                if cls.return_generator:
                    if cls._has_filter and not cls._has_preference:
                        return_statement_str = f"return {get_elements_str}"
                    else:
                        return_statement_str = f"return ({CHOSEN_NAME} for {CHOSEN_NAME} in {get_elements_str})"
                else:
                    if cls._has_filter and not cls._has_preference:
                        return_statement_str = f"return list({get_elements_str})"
                    else:
                        return_statement_str = f"return {get_elements_str}"

        else:
            if cls.no_partition:
                action_args = signature_args[1:]

                if cls._action_arg_spec.has_explicit_return:
                    return_statement_str = (
                        f"return self.action({', '.join(action_args)})"
                    )
                else:
                    return_statement_str = f"self.action({', '.join(action_args)})"
            else:
                raise NotImplementedError()

        generated_call_str += (
            signature_str
            + "\n\t"
            + "\n\t".join(setup_statements)
            + "\n\t"
            + return_statement_str
        )
        cls._generated_call = generated_call_str
        compiled_namespace = cls._compile_fn(generated_call_str, cls.include_globals)
        return compiled_namespace[CALL_METHOD_NAME]

    @classmethod
    def _compile_fn(cls, code_string: str, _globals: dict = None) -> dict:
        """NOTE: THIS SEEMS INCREDIBLY DANGEROUS TO HAVE A FUNCTION COMPILING ARBITRARY CODE.
        TODO: Lock this function away so it's not accessible outside this metaclass.

        Args:
            code_string (str): code to be compiled.
            _globals (dict, optional): globals to be included in the compilation step. Defaults to None.

        Returns:
            dict: compiled namespace variables.
        """
        if _globals is None:
            _globals = dict()
        _locals = {}
        _globals["cmp_to_key"] = cmp_to_key
        _globals["nlargest"] = nlargest
        _globals["nsmallest"] = nsmallest
        eval(
            compile(
                code_string,
                "<string>",
                "exec",
            ),
            _globals,
            _locals,
        )
        return _locals


class Controller(metaclass=MetaController): ...


if __name__ == "__main__":
    import random

    random.seed(0)

    class TestController(Controller):
        counter = 0
        # return_generator = True
        # static_mode = True

        def action(self, chosen: int, arg0, kwarg0=0) -> tuple:
            # self.counter += 1
            return chosen  # , self.counter

        @staticmethod
        def filter(chosen: int, *args) -> bool:
            return chosen % 2 == 0

        @staticmethod
        def preference(a: int, b: int, **kwargs) -> int:
            return -1 if a < b else 1 if a > b else 0

    elements = (random.randint(0, 100000) for _ in range(1000))
    tst = TestController()
    # result = TestController(elements)
    result = tst(elements)
    pass
