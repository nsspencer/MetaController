import inspect
import random
import time
import timeit
from functools import cmp_to_key
from heapq import nsmallest

from pycontroller import quicksort

random.seed(0)
elements = [random.randint(0, 10000000) for _ in range(100_00000)]
num_iterations = 1


def action_fn(chosen: int, arg0: int) -> int:
    return chosen


def filter_fn(chosen: int, special_val: int = 1) -> int:
    return chosen % 2 == 0 if chosen != special_val else False


def preference_fn(a: int, b: int, arg0) -> int:
    if a == arg0:
        return -1
    if b == arg0:
        return 1
    return -1 if a < b else 1 if b > a else 0


def wrap_action_function(fn, arg0):
    def wrapper(chosen):
        return fn(chosen, arg0)

    return wrapper


def wrap_preference_function(fn, arg0):
    def wrapper(a, b):
        return fn(a, b, arg0)

    return wrapper


def wrap_filter_function(fn, special_val=1):
    def wrapper(chosen):
        return fn(chosen, special_val=special_val)

    return wrapper


def action_no_filter_no_preference(elements: list, arg0: int) -> list:
    a_fn = action_fn
    return [a_fn(chosen, arg0) for chosen in elements]


def action_generator_no_filter_no_preference(elements: list, arg0: int) -> list:
    a_fn = action_fn
    return list(a_fn(chosen, arg0) for chosen in elements)


def action_map_no_filter_no_preference(elements, arg0) -> list:
    a_fn = action_fn
    return list(map(wrap_action_function(a_fn, arg0), elements))


def action_with_filter_no_preference(
    elements: list, arg0: int, special_val: int = 1
) -> list:
    return [
        action_fn(chosen, arg0)
        for chosen in (
            chosen for chosen in elements if filter_fn(chosen, special_val=special_val)
        )
    ]


def action_with_wrapped_filter_no_preference(
    elements: list, arg0: int, special_val: int = 1
) -> list:
    return [
        action_fn(chosen, arg0)
        for chosen in filter(
            wrap_filter_function(filter_fn, special_val=special_val), elements
        )
    ]


def action_with_filter_with_preference(
    elements: list, arg0: int, special_val: int = 1
) -> list:
    a_fn = action_fn
    return [
        a_fn(chosen, arg0)
        for chosen in sorted(
            filter(filter_fn, elements),
            key=cmp_to_key(wrap_preference_function(preference_fn, arg0)),
        )
    ]


def simple_pref_sort(a, b):
    return -1 if a < b else 1 if a > b else 0


def simple_pref_sort_unused_extra_arg(a, b, c):
    return -1 if a < b else 1 if a > b else 0


print(
    "quicksort with comp",
    "\t\t\t",
    timeit.timeit(
        lambda: quicksort.quickSort(elements, simple_pref_sort),
        number=num_iterations,
    ),
)
print(
    "quicksort with wrapped comp",
    "\t\t",
    timeit.timeit(
        lambda: quicksort.quickSort(
            elements, wrap_preference_function(preference_fn, 1)
        ),
        number=num_iterations,
    ),
)

print(
    "timsort",
    "\t\t\t\t",
    timeit.timeit(
        lambda: quicksort.timSort2(elements),
        number=num_iterations,
    ),
)
print(
    "timsort with comp",
    "\t\t\t",
    timeit.timeit(
        lambda: quicksort.timSort(elements, simple_pref_sort),
        number=num_iterations,
    ),
)
print(
    "timsort with wrapped comp",
    "\t\t",
    timeit.timeit(
        lambda: quicksort.timSort(elements, wrap_preference_function(preference_fn, 1)),
        number=num_iterations,
    ),
)

print(
    "sorted",
    "\t\t\t\t\t",
    timeit.timeit(lambda: sorted(elements), number=num_iterations),
)
print(
    "sorted with cmp",
    "\t\t\t",
    timeit.timeit(
        lambda: sorted(elements, key=cmp_to_key(simple_pref_sort)),
        number=num_iterations,
    ),
)
print(
    "sorted wrapped cmp",
    "\t\t\t",
    timeit.timeit(
        lambda: sorted(
            elements, key=cmp_to_key(wrap_preference_function(preference_fn, 1))
        ),
        number=num_iterations,
    ),
)


print(
    "nsmallest",
    "\t\t\t\t",
    timeit.timeit(
        lambda: nsmallest(1, elements),
        number=num_iterations,
    ),
)
print(
    "nsmallest with cmp",
    "\t\t\t",
    timeit.timeit(
        lambda: nsmallest(1, elements, key=cmp_to_key(simple_pref_sort)),
        number=num_iterations,
    ),
)
print(
    "nsmallest wrapped cmp",
    "\t\t\t",
    timeit.timeit(
        lambda: nsmallest(
            1,
            elements,
            key=cmp_to_key(wrap_preference_function(preference_fn, 1)),
        ),
        number=num_iterations,
    ),
)

print(
    "min",
    "\t\t\t\t",
    timeit.timeit(
        lambda: min(elements),
        number=num_iterations,
    ),
)
print(
    "min with cmp",
    "\t\t\t",
    timeit.timeit(
        lambda: min(elements, key=cmp_to_key(simple_pref_sort)),
        number=num_iterations,
    ),
)
print(
    "min wrapped cmp",
    "\t\t\t",
    timeit.timeit(
        lambda: min(
            elements,
            key=cmp_to_key(wrap_preference_function(preference_fn, 1)),
        ),
        number=num_iterations,
    ),
)


# special_val = 1
# argument = 1
# a = timeit.timeit(
#     lambda: action_no_filter_no_preference(elements, argument),
#     number=num_iterations,
# )
# a2 = timeit.timeit(
#     lambda: action_map_no_filter_no_preference(elements, argument), number=num_iterations
# )
# a3 = timeit.timeit(
#     lambda: action_generator_no_filter_no_preference(elements, argument), number=num_iterations
# )
# b = timeit.timeit(
#     lambda: action_with_filter_no_preference(
#         elements, argument, special_val=special_val
#     ),
#     number=num_iterations,
# )
# b2 = timeit.timeit(
#     lambda: action_with_wrapped_filter_no_preference(
#         elements, argument, special_val=special_val
#     ),
#     number=num_iterations,
# )
# c = timeit.timeit(
#     lambda: action_with_filter_with_preference(
#         elements, argument, special_val=special_val
#     ),
#     number=num_iterations,
# )
# print(a, a2, a3, b, b2, c)


"""
FINDINGS:

action:
With args, the fastest way is to assign a local variable to the action fn and then call that in a list comprehension, passing the args required by name and by kwarg.

preference:
TLDR: For now, just use nsmallest everywhere to avoid needing a c compiler for my cython code.
Without args, sorted is the fastest, with nsmallest with the length of the elements being almost equivalent. With a comparitor, my cython implementation of timsort
with a comparator is fastest, then nsmallest is 20% slower, then sorted with a comparator just behind at 22%. With a comparitor with args, my cython timsort is about 
25% faster than nsmallest with a wrapped comparator, and about 28% faster than sorted with a wrapped comparitor.


filter:
TODO


first cases:

action:
chosen arg
additional arguments

filter:
chosen arg
additional arguments

preference:



"""
