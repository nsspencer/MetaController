import ast
from abc import ABC, abstractmethod


class BaseControlledMethod(ABC):
    @abstractmethod
    def get_invocation(self) -> ast.AST:
        """
        Generates the code required to use this controlled method.

        The return value is the invocation of this controlled method, which is the way
        it is used.

        Returns:
            ast.AST: Invocation call of this controlled method
        """
        ...

    @abstractmethod
    def get_setup_statements(self) -> list[ast.AST]:
        """
        Generates and returns a list of setup statements for this controlled method to work.
        It is valid for the controlled method to have no setup statements, in such a case, this
        method will return an empty list.

        Returns:
            list[ast.AST]: List of setup statements required for this controlled method to work. Empty
            list if none are required.
        """
        ...
