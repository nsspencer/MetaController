import random
import time
import timeit
from functools import cmp_to_key

random.seed(0)

elements = [random.randint(0, 10000000) for _ in range(100000)]


def action_fn(chosen: int) -> int:
    return chosen


def filter_fn(chosen: int) -> int:
    return chosen % 2 == 0


def preference_fn(a: int, b: int) -> int:
    return -1 if a < b else 1 if b > a else 0


def action_no_filter_no_preference(elements: list) -> list:
    a_fn = action_fn
    return [a_fn(chosen) for chosen in elements]


def action_map_no_filter_no_preference(elements) -> list:
    return list(map(action_fn, elements))


def action_with_filter_no_preference(elements: list) -> list:
    f_fn = filter_fn
    a_fn = action_fn
    return [a_fn(chosen) for chosen in filter(f_fn, elements)]


def action_with_generator_filter_no_preference(elements: list) -> list:
    f_fn = filter_fn
    a_fn = action_fn
    return [a_fn(chosen) for chosen in (chosen for chosen in elements if f_fn(chosen))]


def action_with_filter_with_preference(elements: list) -> list:
    a_fn = action_fn
    return [
        a_fn(chosen)
        for chosen in sorted(filter(filter_fn, elements), key=cmp_to_key(preference_fn))
    ]


a = timeit.timeit(lambda: action_no_filter_no_preference(elements), number=100)
a2 = timeit.timeit(lambda: action_map_no_filter_no_preference(elements), number=100)
b = timeit.timeit(lambda: action_with_filter_no_preference(elements), number=100)
b2 = timeit.timeit(
    lambda: action_with_generator_filter_no_preference(elements), number=100
)
c = timeit.timeit(lambda: action_with_filter_with_preference(elements), number=100)
print(a, a2, b, b2, c)
