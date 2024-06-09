import ast

from ._base import BaseControlledMethod


class PreController(BaseControlledMethod):
    def get_invocation(self) -> ast.AST:
        # TODO
        ...

    def get_setup_statements(self) -> list[ast.AST]:
        # TODO
        ...
