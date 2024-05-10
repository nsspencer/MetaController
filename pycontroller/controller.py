import ast
import inspect
import warnings
from functools import cmp_to_key
from heapq import _heapify_max, heapify, nlargest, nsmallest
from textwrap import dedent
from typing import Callable

PARTITION_NAME = "partition"
CHOSEN_NAME = "chosen"
ABBREVIATED_FILTER_FN = "__f"
ABBREVIATED_PREFERENCE_FN = "__p"
ABBREVIATED_ACTION_FN = "__a"


class SignatureHelper:
    def __init__(self, fn: Callable) -> None:
        self.spec = inspect.getfullargspec(fn)
        self.has_explicit_return = SignatureHelper.fn_has_explicit_return(fn)

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
    no_input = False
    return_generator = False
    max_chosen = None
    use_simple_sort = False
    reverse_sort = False
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

        if "filter" in attrs:
            cls._has_filter = True
            cls._filter_arg_spec = SignatureHelper(attrs["filter"])

        if "preference" in attrs:
            cls._has_preference = True
            cls._preference_arg_spec = SignatureHelper(attrs["preference"])

        MetaController.validate_methods(cls, attrs)
        call_fn = MetaController.generate_call_method(cls)
        cls.__call__ = call_fn

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
            required_length = 2
            if cls.no_input:
                required_length = 1
            if len(cls._action_arg_spec.positional_args) < required_length:
                raise TypeError(
                    '"action" requires a minimum of 2 arguments: "self" and "chosen".'
                )

        if "filter" in attrs:
            if cls.no_input:
                raise ValueError('"filter" not supported in "no_input" mode.')

            if not cls._filter_arg_spec.has_explicit_return:
                raise ValueError("filter requires a boolean return value.")

            if len(cls._filter_arg_spec.positional_args) < 2:
                raise TypeError(
                    '"filter" requires a minimum of 2 arguments: "self" and "chosen".'
                )

        if "preference" in attrs:
            if cls.no_input:
                raise ValueError('"preference" not supported in "no_input" mode.')

            if not cls._preference_arg_spec.has_explicit_return:
                raise ValueError("preference requires a boolean return value.")

            if len(cls._preference_arg_spec.positional_args) < 3:
                raise TypeError(
                    '"preference" requires a minimum of 2 arguments: "self", "a", and "b".'
                )

    @staticmethod
    def generate_call_method(cls: "MetaController") -> Callable:

        signature_args = ["self"]
        if cls.no_input == False:
            signature_args.append(PARTITION_NAME)

        # TODO: do something smarter with named positional arguments and keyword paramters
        # since unpacking is slow
        needs_args = False
        if cls._has_action:
            _action_arg_requirement = 1 if cls.no_input else 2
            if (
                len(cls._action_arg_spec.positional_args) != _action_arg_requirement
            ) or (cls._action_arg_spec.has_arg_unpack):
                needs_args = True

        if cls._has_filter:
            if (len(cls._filter_arg_spec.positional_args) != 2) or (
                cls._filter_arg_spec.has_arg_unpack
            ):
                needs_args = True

        if cls._has_preference:
            if (len(cls._preference_arg_spec.positional_args) != 3) or (
                cls._preference_arg_spec.has_arg_unpack
            ):
                needs_args = True

        if needs_args:
            signature_args.append("*args")

        # TODO: do something smarter with named positional arguments and keyword paramters
        # since unpacking is slow
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
        signature_str = f"def _call_me_({', '.join(signature_args)}):"

        # check for the speedy happy path
        setup_statements = []
        if needs_args == False and needs_kwargs == False:

            get_elements_str = PARTITION_NAME
            if cls._has_filter:
                setup_statements.append(f"{ABBREVIATED_FILTER_FN} = self.filter")
                get_elements_str = (
                    f"filter({ABBREVIATED_FILTER_FN}, " + get_elements_str + ")"
                )
            if cls._has_preference and cls.max_chosen is None:
                setup_statements.append(
                    f"{ABBREVIATED_PREFERENCE_FN} = self.preference"
                )
                if cls.reverse_sort:
                    get_elements_str = f"sorted({get_elements_str}, key=cmp_to_key({ABBREVIATED_PREFERENCE_FN}), reverse=True)"
                else:
                    get_elements_str = f"sorted({get_elements_str}, key=cmp_to_key({ABBREVIATED_PREFERENCE_FN}))"

            elif cls._has_preference and cls.max_chosen is not None:
                raise NotImplementedError()

            return_statement_str = ""
            if cls._has_action:
                setup_statements.append("__a = self.action")
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
        return compiled_namespace["_call_me_"]

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
        _globals["heapify"] = heapify
        _globals["cmp_to_key"] = cmp_to_key
        ns = {}
        eval(
            compile(
                code_string,
                "<string>",
                "exec",
            ),
            _globals,
            ns,
        )
        return ns


class Controller(metaclass=MetaController): ...


if __name__ == "__main__":
    import random

    random.seed(0)

    class TestController(Controller):
        counter = 0
        return_generator = True

        def action(self, chosen: int) -> tuple:
            self.counter += 1
            return chosen, self.counter

        def filter(self, chosen: int) -> bool:
            return chosen % 2 == 0

        def preference(self, a: int, b: int) -> int:
            return -1 if a < b else 1 if a > b else 0

    elements = (random.randint(0, 100000) for _ in range(1000))
    tst = TestController()
    result = tst(elements)
    pass
