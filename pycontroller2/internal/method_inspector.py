import ast
import inspect
import warnings
from textwrap import dedent
from typing import Callable


class MethodInspector:
    def __init__(self, func: Callable) -> None:
        self.func = func
        self.__has_explicit_void_return = False
        self.__has_explicit_value_return = False
        self.__has_value_yield = False
        self.__has_value_yield_from = False
        self.__error = False
        self._parse()

    ###
    # Read Only Properties
    #

    @property
    def has_explicit_void_return(self) -> bool:
        return self.__has_explicit_void_return

    @property
    def has_explicit_value_return(self) -> bool:
        return self.__has_explicit_value_return

    @property
    def has_value_yield(self) -> bool:
        return self.__has_value_yield

    @property
    def has_value_yield_from(self) -> bool:
        return self.__has_value_yield_from

    @property
    def has_parse_error(self) -> bool:
        return self.__error

    def _parse(self) -> None:
        """Inspection method to parse this instances' callable and determine the
        different ways it can exit:

        Explicit Void returns are when a return statement with no value is provided in the top
        level scope of the provided method.

        Explicit Value returns are when a return statement with a right hand value
        (including None) is provided in the top level scope of the method.

        Value Yield and Value Yield From are equivalent to the checks above, but for
        the yield and yield from keywords.
        """
        try:
            source = inspect.getsource(self.func)
            module = ast.parse(dedent(source))

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
            visitor.visit(module.body[0])  # Only visit the top-level function

            self.__has_explicit_value_return = visitor.has_explicit_value_return
            self.__has_explicit_void_return = visitor.has_explicit_void_return
            self.__has_value_yield = visitor.has_value_yield
            self.__has_value_yield_from = visitor.has_value_yield_from

        except BaseException as err:
            try:
                name = self.func.__name__
            except BaseException:
                name = "UNKNOWN"
            warnings.warn(f'Unable to parse callable "{name}". Error message: {err}')
            self.__error = True


if __name__ == "__main__":

    def test():
        class TestClass:
            def test2():
                return 0

        yield TestClass

    result = MethodInspector(test)
    print(result.has_explicit_value_return)
    print(result.has_explicit_void_return)
    print(result.has_value_yield)
    print(result.has_value_yield_from)
    print(result.has_parse_error)
