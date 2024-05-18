import random
import timeit
from dataclasses import dataclass
from functools import cmp_to_key
from typing import Any

from pycontroller import Controller

random.seed(0)
num_times = 100


def create_class():
    class MyController(Controller):
        # @staticmethod
        # def do_work():
        #     return 1

        # @staticmethod
        # def action(chosen: Any) -> Any:
        #     return chosen + MyController.do_work()

        # @staticmethod
        # def filter(chosen: Any) -> bool:
        #     return True

        @staticmethod
        def preference(a: Any, b: Any) -> int:
            return -1 if a < b else 1 if a > b else 0

    return MyController


cls = create_class()


def construct(cls=cls):
    return cls()


@dataclass
class Data:
    data: int

    def __lt__(self, other):
        return self.data < other.data

    def __add__(self, other):
        self.data += other


if __name__ == "__main__":
    print(timeit.timeit(lambda: create_class(), number=num_times))
    print(timeit.timeit(lambda: construct(), number=num_times))

    inst = construct()
    elements = list(Data(random.randint(0, 10000000)) for _ in range(10_0000))
    print(timeit.timeit(lambda: sorted(elements), number=num_times))
    print(
        timeit.timeit(
            lambda: sorted(elements, key=cmp_to_key(cls.preference)), number=num_times
        )
    )
    print(timeit.timeit(lambda: inst(elements), number=num_times))
