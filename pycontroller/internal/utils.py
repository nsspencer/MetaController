import ast
from typing import List

from pycontroller.internal.namespace import POSITIONAL_ARG_PREFIX


def generate_positional_args(num_args: int) -> List[ast.arg]:
    """
    Generates positional args using the positional arg prefix defined above.

    Args:
        num_args (int): Number of args to generate

    Returns:
        List[ast.arg]: list of generated ast.args
    """
    args = []

    for i in range(num_args):
        args.append(
            ast.arg(
                arg=f"{POSITIONAL_ARG_PREFIX}{i}",
                annotation=None,
                type_comment=None,
            )
        )
    return args
