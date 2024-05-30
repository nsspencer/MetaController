import ast
import inspect
import warnings
from textwrap import dedent
from typing import Any, Callable, List, Tuple


class SignatureHelper:
    def __init__(self, fn: Callable) -> None:
        if hasattr(fn, "__wrapped__"):
            self.spec = inspect.getfullargspec(fn.__wrapped__)
            self.is_wrapped = True
        else:
            self.spec = inspect.getfullargspec(fn)
            self.is_wrapped = False
        self.is_staticmethod = isinstance(fn, staticmethod)
        self.fn = fn
        self._signature_dict = self.signature_to_dict(self.fn)

    @staticmethod
    def signature_to_dict(fn: Callable) -> dict:
        """
        returns a dict with the following keys:
        'posonlyargs', 'args', 'varargs', 'varkw', 'defaults', 'kwonlyargs', 'kwonlydefaults', 'annotations'

        NOTE: if "posonlyargs" exists, they will also be found in "args".

        Args:
            fn (Callable): callable object

        Returns:
            dict: dictionary with the components of the call signature
        """
        result = {}
        result["posonlyargs"] = [
            name
            for name, param in inspect.signature(fn).parameters.items()
            if param.kind == inspect.Parameter.POSITIONAL_ONLY
        ]
        result.update(inspect.getfullargspec(fn)._asdict())
        return result

    @property
    def posonlyargs(self) -> list:
        return self._signature_dict["posonlyargs"]

    @property
    def args(self) -> list:
        return self._signature_dict["args"]

    @property
    def varargs(self) -> list:
        return self._signature_dict["varargs"]

    @property
    def varkw(self) -> list:
        return self._signature_dict["varkw"]

    @property
    def defaults(self) -> list:
        return self._signature_dict["defaults"] or list()

    @property
    def kwonlyargs(self) -> list:
        return self._signature_dict["kwonlyargs"]

    @property
    def kwonlydefaults(self) -> list:
        return self._signature_dict["kwonlydefaults"] or list()

    @property
    def annotations(self) -> list:
        return self._signature_dict["annotations"] or list()

    def get_defaulted_args(self) -> List[Tuple[str, Any]]:
        """
        Returns a list of tuples of (str,Any) being the argument name and its default.

        Returns:
            List[Tuple[str, Any]]: defaulted argument names and values
        """
        keywords = self.args[len(self.args) - len(self.defaults) :]
        if len(keywords) == 0:
            return list()

        return list(zip(keywords, self.defaults))

    def get_keyword_only_args(self) -> List[Tuple[str, Any]]:
        """
        Returns a list of tuples of (str,Any) being the keyword and its value.

        Returns:
            List[Tuple]: keyword only argument names and values
        """
        if len(self.kwonlyargs) == 0:
            return list()

        return list(self.kwonlydefaults.items())

    @property
    def has_arg_unpack(self):
        return self.spec[1] is not None

    @property
    def has_kwarg_unpack(self):
        return self.spec[2] is not None

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
