import random

random.seed(0)
import heapq
import timeit
from functools import cmp_to_key, partial


def preference(a, b) -> int:
    return -1 if a < b else 1 if a > b else 0


class TestClass:
    __slots__ = "obj"

    def __init__(self, obj) -> None:
        self.obj = obj

    def __lt__(self, other):
        return self.obj < other.obj

    def __gt__(self, other):
        return self.obj > other.obj


def test_preference(a: TestClass, b: TestClass) -> int:
    return -1 if a.obj < b.obj else 1 if a.obj > b.obj else 0


def test1():
    elements = [random.randint(0, 1000000) for _ in range(10_000_000)]
    test_elements = [TestClass(i) for i in elements]
    num_times = 1

    print("Built in types")
    print(timeit.timeit(lambda: sorted(elements), number=num_times))
    print(
        timeit.timeit(
            lambda: sorted(elements, key=cmp_to_key(preference)), number=num_times
        )
    )

    print("Custom types")
    print(timeit.timeit(lambda: sorted(test_elements), number=num_times))
    print(
        timeit.timeit(
            lambda: sorted(test_elements, key=cmp_to_key(test_preference)),
            number=num_times,
        )
    )
    print(
        timeit.timeit(
            lambda: heapq.nsmallest(
                100000,
                filter(lambda x: x.obj % 2 == 0, test_elements),
                key=cmp_to_key(test_preference),
            ),
            number=num_times,
        )
    )


def test2():

    elements = [random.randint(0, 1000000) for _ in range(1_000_000)]
    number = 10

    def normal_filter(chosen):
        return chosen % 1 == 0

    def wrapped_filter(pos_arg):
        def inner_filter(chosen):
            return chosen % pos_arg == 0

        return inner_filter

    def filter_with_arg(chosen, arg):
        return chosen % arg == 0

    def wrapped_filter_with_arg(pos_arg):
        def wrapped_filter(chosen):
            return filter_with_arg(chosen, pos_arg)

        return wrapped_filter

    print(timeit.timeit(lambda: list(filter(normal_filter, elements)), number=number))
    print(
        timeit.timeit(lambda: list(filter(wrapped_filter(1), elements)), number=number)
    )
    print(
        timeit.timeit(
            lambda: list(filter(wrapped_filter_with_arg(1), elements)), number=number
        )
    )

    lambda_filter_func = lambda chosen: filter_with_arg(chosen, 1)
    print(
        timeit.timeit(lambda: list(filter(lambda_filter_func, elements)), number=number)
    )
    print(
        timeit.timeit(
            lambda: list(i for i in elements if filter_with_arg(i, 1)), number=number
        )
    )


if __name__ == "__main__":
    test2()
