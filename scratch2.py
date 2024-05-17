import random

random.seed(0)
import heapq
import timeit
from functools import cmp_to_key


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


if __name__ == "__main__":
    elements = [random.randint(0, 1000000) for _ in range(10_000_000)]
    test_elements = [TestClass(i) for i in elements]
    num_times = 1

    # print("Built in types")
    # print(timeit.timeit(lambda: sorted(elements), number=num_times))
    # print(
    #     timeit.timeit(
    #         lambda: sorted(elements, key=cmp_to_key(preference)), number=num_times
    #     )
    # )

    print("Custom types")
    # print(timeit.timeit(lambda: sorted(test_elements), number=num_times))
    # print(
    #     timeit.timeit(
    #         lambda: sorted(test_elements, key=cmp_to_key(test_preference)),
    #         number=num_times,
    #     )
    # )
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
