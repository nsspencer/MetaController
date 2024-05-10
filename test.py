import dis
import random
import time
import timeit

from pycontroller import DoAllController, DoController

random.seed(0)


class MyController(DoController):
    def action(self, element: int) -> None:
        return element % 2 == 0


class DoAll(DoAllController):
    def filter(self, chosen: int) -> bool:
        return chosen % 2 == 0

    def action(self, chosen: int):
        return chosen


elements = [random.randint(0, 100000) for _ in range(200000)]

controller = MyController()
all_controller = DoAll()
# print(timeit.timeit(lambda: [i for i in elements if i % 2 == 0], number=100))
# print(timeit.timeit(lambda: controller(elements), number=100))


class test:
    def __init__(self, val) -> None:
        self.val = val

    def __add__(self, other):
        self.val += other

    def __repr__(self):
        return str(self.val)


data = test(0)


def work(element: int):
    return element % 2 == 0


v = all_controller(elements)

print(timeit.timeit(lambda: [i for i in elements if controller(i)], number=100))
print(timeit.timeit(lambda: list(all_controller(elements)), number=100))
print(timeit.timeit(lambda: [i for i in elements if work(i)], number=100))
print(timeit.timeit(lambda: [i for i in elements if i % 2 == 0], number=100))
print(timeit.timeit(lambda: list(i for i in elements if i % 2 == 0), number=100))
