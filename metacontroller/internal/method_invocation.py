import ast
from typing import List, Tuple

from metacontroller.internal.method_inspector import MethodInspector
from metacontroller.internal.namespace import CLASS_ARG_NAME


class MethodInvocation:
    def __init__(self, method: MethodInspector) -> None:
        self.method = method

    def get_call_args_and_keywords(self) -> Tuple[List[ast.AST], List[ast.keyword]]:
        """
        Generate the call args and keywords for the instance method.

        Returns:
            Tuple[List[ast.AST], List[ast.keyword]]: Tuple of the list of arguments and the list of keywords
            to call this method.
        """
        args = [ast.Name(id=arg, ctx=ast.Load()) for arg in self.method.call_args]
        if self.method.has_arg_unpack:
            args.append(
                ast.Starred(
                    value=ast.Name(id=self.method.varargs, ctx=ast.Load()),
                    ctx=ast.Load(),
                )
            )

        keywords = [
            ast.keyword(arg=keyword, value=ast.Name(id=keyword, ctx=ast.Load()))
            for keyword, _ in self.method.get_keyword_only_args()
        ]

        if self.method.has_kwarg_unpack:
            keywords.append(
                ast.keyword(
                    arg=None, value=ast.Name(id=self.method.varkw, ctx=ast.Load())
                )
            )
        return args, keywords

    def to_function_call(
        self,
        args: List[ast.AST] = None,
        keywords: List[ast.keyword] = None,
        name: str = None,
    ) -> ast.Call:
        """
        Generates the invocation call for this method, assuming the arguments
        being passed in are the same name as the parameters defined in this
        function.

        Returns:
            ast.Call: ast representation of a Callable that will call this instances method.
            This should be wrapped in an ast.Expr before compiling.
        """

        if args is None or keywords is None:
            __args, __keywords = self.get_call_args_and_keywords()
            if args is None:
                args = __args
            if keywords is None:
                keywords = __keywords

        if name is None:
            _name = self.method.name
        else:
            _name = name
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                attr=_name,
                ctx=ast.Load(),
            ),
            args=args,
            keywords=keywords,
        )

    def to_lambda(self, lambda_args: List[str], name: str = None) -> ast.Lambda:
        args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=arg, annotation=None) for arg in lambda_args],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )
        return ast.Lambda(args=args, body=self.to_function_call(name=name))
