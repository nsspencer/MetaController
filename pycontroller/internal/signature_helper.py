import ast
import inspect
import warnings
from textwrap import dedent
from typing import Callable


class SignatureHelper:
    def __init__(self, fn: Callable) -> None:
        if hasattr(fn, "__wrapped__"):
            self.spec = inspect.getfullargspec(fn.__wrapped__)
            self.is_wrapped = True
        else:
            self.spec = inspect.getfullargspec(fn)
            self.is_wrapped = False
        self.has_explicit_return = SignatureHelper.fn_has_explicit_return(fn)
        self.is_staticmethod = isinstance(fn, staticmethod)

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
