import ast
import inspect
import warnings
from functools import cmp_to_key
from heapq import nlargest, nsmallest
from textwrap import dedent
from typing import Callable

PARTITION_NAME = "partition"
CHOSEN_NAME = "chosen"
ABBREVIATED_FILTER_FN = "f"
ABBREVIATED_PREFERENCE_FN = "p"
ABBREVIATED_ACTION_FN = "a"
CALL_METHOD_NAME = "_call_me_"


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
        return self.spec[3]

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


class MetaController(type):
    name = None
    no_partition = False
    return_generator = False
    max_chosen = None
    use_simple_sort = False
    reverse_sort = False
    static_mode = False
    include_globals = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name == "Controller":
            return

        cls.name: str = cls.name or name
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
            # TODO: This might be able to be improved for speed
            cls.__call__ = call_fn

            def new(cls, *args, **kwargs):
                return cls.__call__(cls, *args, **kwargs)

            cls.__new__ = new
        else:
            cls.__call__ = call_fn

    @staticmethod
    def validate_attributes(cls: "MetaController", attrs: dict) -> None:
        if cls.no_partition:
            if cls.max_chosen is not None:
                raise AttributeError(
                    'Cannot have "no_partition" and "max_chosen" defined together.'
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
    def generate_call_method(cls: "MetaController") -> Callable:

        signature_args = ["self"]
        if cls.no_partition == False:
            signature_args.append(PARTITION_NAME)

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

            if cls.max_chosen and not max_chosen_handled:
                get_elements_str = get_elements_str + f"[:{cls.max_chosen}]"

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

        @staticmethod
        def action(chosen: int) -> tuple:
            # self.counter += 1
            return chosen  # , self.counter

        @staticmethod
        def filter(chosen: int) -> bool:
            return chosen % 2 == 0

        @staticmethod
        def preference(a: int, b: int) -> int:
            return -1 if a < b else 1 if a > b else 0

    elements = (random.randint(0, 100000) for _ in range(1000))
    tst = TestController()
    # result = TestController(elements)
    result = tst(elements)
    pass
