import ast
from functools import cmp_to_key
from typing import Any, Callable

from metacontroller.internal.exceptions import (
    InvalidControllerMethodError,
    InvalidReturnError,
)
from metacontroller.internal.method_invocation import MethodInvocation
from metacontroller.internal.namespace import (
    ACTION_METHOD_NAME,
    ACTION_RESULT_ASSIGNMENT_NAME,
    CLASS_ARG_NAME,
    FILTER_METHOD_NAME,
    FOLD_METHOD_NAME,
    GENERATED_CALL_METHOD_NAME,
    PARTITION_ARG_NAME,
    POST_CONTROLLER_METHOD_NAME,
    PRE_CONTROLLER_METHOD_NAME,
    SORT_CMP_METHOD_NAME,
    SORT_KEY_METHOD_NAME,
)

from ._base import BaseControllerImplementation


class DoAllImplementation(BaseControllerImplementation):
    def __init__(self, cls, name, bases, attrs, stack_frame) -> None:
        super().__init__(cls, name, bases, attrs, stack_frame)

    def validate(self) -> None:
        super().validate()
        if self.has_sort_key and self.has_sort_cmp:
            err = f'DoAll controller "{self.name}" is invalid because both sort methods ("{SORT_KEY_METHOD_NAME}" and "{SORT_CMP_METHOD_NAME}") are defined.'
            err += f' You must define only one. Note that "{SORT_KEY_METHOD_NAME}" is more performant.'
            raise InvalidControllerMethodError(err)

        if self.has_filter:
            if len(self.filter.call_args) < 1:
                raise AttributeError(
                    f'"{FILTER_METHOD_NAME}" should be defined with at least 1 non-class argument (chosen), but 0 were given.'
                )

        if self.has_sort_key:
            if len(self.sort_key.call_args) < 1:
                raise AttributeError(
                    f'"{SORT_KEY_METHOD_NAME}" should be defined with at least 1 non-class argument (chosen), but 0 were given.'
                )

        if self.has_sort_cmp:
            if len(self.sort_cmp.call_args) < 2:
                raise AttributeError(
                    f'"{SORT_CMP_METHOD_NAME}" should be defined with at least 2 non-class arguments (a, b), but {len(self.sort_cmp.call_args)} were given.'
                )

        if self.has_action:
            if len(self.action.call_args) < 1:
                raise AttributeError(
                    f'"{ACTION_METHOD_NAME}" should be defined with at least 1 non-class argument (chosen), but 0 were given.'
                )

        if self.has_fold:
            if len(self.fold.call_args) < 1:
                raise AttributeError(
                    f'"{FOLD_METHOD_NAME}" should be defined with at least 1 non-class argument (list of action results), but 0 were given.'
                )

            if self.has_action and not self.action.returns_a_value:
                raise InvalidReturnError(
                    f'"{FOLD_METHOD_NAME}" was defined, but "{ACTION_METHOD_NAME}" does not return anything.'
                )

    def generate_call_method(self) -> Callable[..., Any]:
        body = []
        additional_globals = {}
        get_elements = ast.Name(id=PARTITION_ARG_NAME, ctx=ast.Load())

        if self.has_pre_controller:
            pre_controller_call = MethodInvocation(
                self.pre_controller
            ).to_function_call(name=PRE_CONTROLLER_METHOD_NAME)
            body.append(ast.Expr(value=pre_controller_call))

        if self.has_filter:
            if self.filter.num_call_parameters != 1:
                filter_fn = MethodInvocation(self.filter).to_lambda(
                    [self.filter.call_args[0]], name=FILTER_METHOD_NAME
                )
            else:
                filter_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=FILTER_METHOD_NAME,
                    ctx=ast.Load(),
                )
            get_elements = ast.Call(
                func=ast.Name(id="filter", ctx=ast.Load()),
                args=[filter_fn, get_elements],
                keywords=[],
            )

        if self.has_sort_key:
            if self.sort_key.num_call_parameters != 1:
                sort_fn = MethodInvocation(self.sort_key).to_lambda(
                    [self.sort_key.call_args[0]], name=SORT_KEY_METHOD_NAME
                )
            else:
                sort_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=SORT_KEY_METHOD_NAME,
                    ctx=ast.Load(),
                )

            sort_keywords = [ast.keyword(arg="key", value=sort_fn)]
            if self.cls.reverse_sort:
                sort_keywords.append(
                    ast.keyword(
                        arg="reverse", value=ast.Constant(value=True, type="bool")
                    )
                )
            get_elements = ast.Call(
                func=ast.Name(id="sorted", ctx=ast.Load()),
                args=[get_elements],
                keywords=sort_keywords,
            )

        if self.has_sort_cmp:
            if self.sort_cmp.num_call_parameters != 2:
                sort_fn = MethodInvocation(self.sort_cmp).to_lambda(
                    self.sort_cmp.call_args[:2], name=SORT_CMP_METHOD_NAME
                )
            else:
                sort_fn = ast.Attribute(
                    value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                    attr=SORT_CMP_METHOD_NAME,
                    ctx=ast.Load(),
                )

            sort_keywords = [
                ast.keyword(
                    arg="key",
                    value=ast.Call(
                        func=ast.Name(id="cmp_to_key", ctx=ast.Load()),
                        args=[sort_fn],
                        keywords=[],
                    ),
                )
            ]
            if self.cls.reverse_sort:
                sort_keywords.append(
                    ast.keyword(
                        arg="reverse", value=ast.Constant(value=True, type="bool")
                    )
                )
            get_elements = ast.Call(
                func=ast.Name(id="sorted", ctx=ast.Load()),
                args=[get_elements],
                keywords=sort_keywords,
            )
            additional_globals["cmp_to_key"] = cmp_to_key

        if self.has_action:
            action_invoke = MethodInvocation(self.action)
            action_args, action_keywords = action_invoke.get_call_args_and_keywords()

            if self.action.returns_a_value:
                # we should capture the results using map
                if self.action.num_call_parameters != 1:
                    # action has additional parameters, use a lambda
                    action_fn = action_invoke.to_lambda(
                        [action_args[0].id], name=ACTION_METHOD_NAME
                    )
                else:
                    # action only takes the required chosen parameter
                    action_fn = ast.Attribute(
                        value=ast.Name(id=CLASS_ARG_NAME, ctx=ast.Load()),
                        attr=ACTION_METHOD_NAME,
                        ctx=ast.Load(),
                    )

                action_call = ast.Call(
                    func=ast.Name(id="list", ctx=ast.Load()),
                    args=[
                        ast.Call(
                            func=ast.Name(id="map", ctx=ast.Load()),
                            args=[action_fn, get_elements],
                            keywords=[],
                        )
                    ],
                    keywords=[],
                )
                action = ast.Assign(
                    targets=[
                        ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())
                    ],
                    value=action_call,
                )
                body.append(action)

            else:
                # no need to capture the result from the action, so use a basic for loop
                action = ast.For(
                    target=ast.Name(id=action_args[0].id, ctx=ast.Store()),
                    iter=get_elements,
                    body=[
                        ast.Expr(
                            value=action_invoke.to_function_call(
                                action_args, action_keywords, name=ACTION_METHOD_NAME
                            )
                        )
                    ],
                    orelse=[],
                )
                body.append(action)

        if self.has_fold:
            fold_invoke = MethodInvocation(self.fold)
            fold_args, fold_keywords = fold_invoke.get_call_args_and_keywords()
            fold_args.pop(0)

            if self.has_action:
                fold_args.insert(
                    0, ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load())
                )
            else:
                fold_args.insert(0, get_elements)

            fold_assignment = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=fold_invoke.to_function_call(
                    fold_args, fold_keywords, name=FOLD_METHOD_NAME
                ),
            )
            body.append(fold_assignment)

        elif not self.has_action:
            # does not have an action, return whatever is get_elements
            if not self.has_sort_cmp and not self.has_sort_key:
                # we need to convert the filter object to a list before we return
                get_elements = ast.Call(
                    func=ast.Name(id="list", ctx=ast.Load()),
                    args=[get_elements],
                    keywords=[],
                )
            get_elements_result = ast.Assign(
                targets=[ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Store())],
                value=get_elements,
            )
            body.append(get_elements_result)

        if self.has_post_controller:
            post_controller_call = MethodInvocation(
                self.post_controller
            ).to_function_call(name=POST_CONTROLLER_METHOD_NAME)
            body.append(ast.Expr(value=post_controller_call))

        if not self.has_fold and (self.has_action and not self.action.returns_a_value):
            pass  # do nothing since we explicitly do not need a return value here
        else:
            body.append(
                ast.Return(
                    value=ast.Name(id=ACTION_RESULT_ASSIGNMENT_NAME, ctx=ast.Load())
                )
            )

        args, saved_defaults = self.get_call_args(
            use_class_arg=True,
            use_k_arg=False,
            use_partition_arg=True,
        )
        additional_globals.update(saved_defaults)
        call_fn = ast.FunctionDef(
            name=GENERATED_CALL_METHOD_NAME,
            args=args,
            body=body,
            decorator_list=[],
            type_params=[],
        )

        module = ast.fix_missing_locations(ast.Module(body=[call_fn], type_ignores=[]))
        return self.compile_call_method(module, additional_globals)
