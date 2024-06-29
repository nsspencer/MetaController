import ast
import inspect
import warnings
from textwrap import dedent
from typing import Any, Callable, List, Tuple


class MethodInspector:
    def __init__(self, fn: Callable) -> None:
        static_override = False
        if not callable(fn):
            abort = True
            try:
                if callable(fn.__func__):
                    abort = False
                    fn = fn.__func__
                    static_override = True
            except BaseException:
                pass

            if abort:
                try:
                    name = fn.__name__
                except AttributeError:
                    name = fn.__func__.__name__
                except BaseException:
                    name = "UNKNOWN"
                raise ValueError(
                    f'MethodInspector expected a callable object, but "{name}" is not.'
                )

        self.fn = fn
        self.__is_staticmethod = isinstance(fn, staticmethod) or static_override
        self.__is_lambda = inspect.isfunction(fn) and fn.__name__ == "<lambda>"

        if hasattr(fn, "__wrapped__"):
            self.spec = inspect.getfullargspec(fn.__wrapped__)
            self._signature_dict = self.signature_to_dict(fn.__wrapped__)
        else:
            self.spec = inspect.getfullargspec(fn)
            self._signature_dict = self.signature_to_dict(fn)

        # set the placeholder values for the return options
        self.__has_explicit_void_return = None
        self.__has_explicit_value_return = None
        self.__has_value_yield = None
        self.__has_value_yield_from = None
        self.__error = None
        self.__decompiled_module = None
        self.__source = None

    ###
    # Read Only Properties
    #

    @property
    def is_staticmethod(self) -> bool:
        return self.__is_staticmethod

    @property
    def is_lambda(self) -> bool:
        return self.__is_lambda

    @property
    def has_explicit_void_return(self) -> bool:
        if self.__has_explicit_void_return is None:
            self._parse_return_options()
        return self.__has_explicit_void_return

    @property
    def has_explicit_value_return(self) -> bool:
        if self.__has_explicit_value_return is None:
            self._parse_return_options()
        if self.is_lambda:
            return True  # lambdas always return a value
        return self.__has_explicit_value_return

    @property
    def has_value_yield(self) -> bool:
        if self.__has_value_yield is None:
            self._parse_return_options()
        return self.__has_value_yield

    @property
    def has_value_yield_from(self) -> bool:
        if self.__has_value_yield_from is None:
            self._parse_return_options()
        return self.__has_value_yield_from

    @property
    def returns_a_value(self) -> bool:
        return (
            self.has_explicit_value_return
            or self.has_value_yield
            or self.has_value_yield_from
        )

    @property
    def has_parse_error(self) -> bool:
        if self.__error is None:
            self._parse_return_options()
        return self.__error

    @property
    def name(self) -> str:
        return self.fn.__name__

    @property
    def posonlyargs(self) -> list:
        """
        Only the position only arguments in the args list.
        """
        return self._signature_dict["posonlyargs"]

    @property
    def args(self) -> list:
        """
        Args are made up of position only and keyword arguments.
        """
        return self._signature_dict["args"] or list()

    @property
    def call_args(self) -> list:
        """
        Call args are made up of arguments excluding the class arg if
        this is an instance method.

        Returns:
            list: _description_
        """
        if self.is_staticmethod:
            return self.args
        return self.args[1:]

    @property
    def num_parameters(self) -> int:
        counter = 0
        counter += len(self.args)
        counter += len(self.kwonlyargs)
        counter += 1 if self.varargs is not None else 0
        counter += 1 if self.varkw is not None else 0
        return counter

    @property
    def num_call_parameters(self) -> int:
        counter = self.num_parameters
        if not self.is_staticmethod:
            counter = max(counter - 1, 0)  # remove the class argument
        return counter

    @property
    def varargs(self) -> str:
        return self._signature_dict["varargs"] or None

    @property
    def varkw(self) -> str:
        return self._signature_dict["varkw"] or None

    @property
    def defaults(self) -> list:
        return self._signature_dict["defaults"] or list()

    @property
    def kwonlyargs(self) -> list:
        return self._signature_dict["kwonlyargs"] or list()

    @property
    def kwonlydefaults(self) -> list:
        return self._signature_dict["kwonlydefaults"] or list()

    @property
    def annotations(self) -> list:
        return self._signature_dict["annotations"] or list()

    @property
    def has_arg_unpack(self):
        return self.varargs is not None

    @property
    def has_kwarg_unpack(self):
        return self.varkw is not None

    @property
    def full_call_arg_spec(self) -> inspect.FullArgSpec:
        if self.__is_staticmethod:
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

    @property
    def body_ast(self) -> List[ast.AST]:
        """
        Returns the body ast of the method. NOTE: This excludes the signature.

        Returns:
            List[ast.AST]: List of AST nodes representing the body of the method.
        """
        if self.has_parse_error:
            return None
        elif self.is_lambda:
            raise NotImplementedError(
                "Inspecting lambda functions is not supported yet."
            )
            # TODO: REPLACE THIS. I should handle lambdas entirely separetely, and boil them down to this class's properties
            return [self.__decompiled_module.body[0].value.body]
        # get the module body, then the body of the function
        return self.__decompiled_module.body[0].body

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

    def get_non_defaulted_args(self) -> List[str]:
        """
        Returns a the list of arguments that are either position only, or non
        defaulted.

        Returns:
            List[str]: Position only or non-defaulted arguments.
        """
        return self.args[: -len(self.get_defaulted_args()) or None]

    def _parse_return_options(self) -> None:
        """Inspection method to parse this instances' callable and determine the
        different ways it can exit:

        Explicit Void returns are when a return statement with no value is provided in the top
        level scope of the provided method.

        Explicit Value returns are when a return statement with a right hand value
        (including None) is provided in the top level scope of the method.

        Value Yield and Value Yield From are equivalent to the checks above, but for
        the yield and yield from keywords.
        """
        # pre-set the values
        self.__has_explicit_void_return = False
        self.__has_explicit_value_return = False
        self.__has_value_yield = False
        self.__has_value_yield_from = False
        self.__error = False

        try:
            self.__source = inspect.getsource(self.fn)
            self.__decompiled_module = ast.parse(dedent(self.__source))

            class InnerReturnVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.has_explicit_void_return = False
                    self.has_explicit_value_return = False
                    self.has_value_yield = False
                    self.has_value_yield_from = False
                    self.__func_hit = False
                    self.__parent_map = {}

                def visit(self, node):
                    if isinstance(node, list):
                        for item in node:
                            if isinstance(item, ast.AST):
                                self.__parent_map[item] = node
                                super().visit(item)
                    elif isinstance(node, ast.AST):
                        for child in ast.iter_child_nodes(node):
                            self.__parent_map[child] = node
                        super().visit(node)

                def visit_Return(self, node):
                    if node.value is not None:
                        self.has_explicit_value_return = True
                    else:
                        self.has_explicit_void_return = True

                def visit_Yield(self, node: ast.Yield):
                    if node.value is not None:
                        self.has_value_yield = True

                def visit_YieldFrom(self, node: ast.YieldFrom):
                    if node.value is not None:
                        self.has_value_yield_from = True

                def visit_FunctionDef(self, node):
                    if self.__func_hit == False:
                        self.__func_hit = True
                        self.generic_visit(node)
                    else:
                        next_node = self.get_next_node(node)
                        if next_node is not None:
                            self.visit(next_node)

                def visit_AsyncFunctionDef(self, node):
                    next_node = self.get_next_node(node)
                    if next_node is not None:
                        self.visit(next_node)

                def visit_Lambda(self, node):
                    next_node = self.get_next_node(node)
                    if next_node is not None:
                        self.visit(next_node)

                def visit_ClassDef(self, node: ast.ClassDef):
                    next_node = self.get_next_node(node)
                    if next_node is not None:
                        self.visit(next_node)

                def get_next_node(self, node):
                    parent = self.__parent_map[node]
                    if hasattr(parent, "body"):
                        next_sibling = (
                            parent.body[parent.body.index(node) + 1]
                            if parent.body.index(node) + 1 < len(parent.body)
                            else None
                        )
                    else:
                        next_sibling = None
                    return next_sibling

            visitor = InnerReturnVisitor()
            visitor.visit(
                self.__decompiled_module.body[0]
            )  # Only visit the top-level function

            self.__has_explicit_value_return = visitor.has_explicit_value_return
            self.__has_explicit_void_return = visitor.has_explicit_void_return
            self.__has_value_yield = visitor.has_value_yield
            self.__has_value_yield_from = visitor.has_value_yield_from
            self.__error = False

        except BaseException as err:
            try:
                name = self.fn.__name__
            except BaseException:
                name = "UNKNOWN"
            warnings.warn(f'Unable to parse callable "{name}". Error message: {err}')
            self.__error = True

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


if __name__ == "__main__":

    def test():
        class TestClass:
            def test2(self):
                return 0

            __call__ = lambda: print("called")

        yield (lambda: TestClass)()

    # import timeit
    # print(timeit.timeit(lambda: MethodInspector(test).has_parse_error, number=1000))

    lambda_test = lambda: print("test")
    r = MethodInspector(lambda_test)
    syntax = r.body_ast
    result = MethodInspector(test)
    print(result.has_explicit_value_return)
    print(result.has_explicit_void_return)
    print(result.has_value_yield)
    print(result.has_value_yield_from)
    print(result.has_parse_error)
