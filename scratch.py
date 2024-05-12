import functools
import heapq
import random
import time
from functools import partial

import pycontroller.internal

random.seed(0)


elements = [random.randint(0, 100000) for _ in range(2_000_00)]


def time_tests1():

    # def action_fn(chosen):
    #     # print(f"{chosen} {arg1} {action_arg}")
    #     # return (chosen, arg1, action_arg)
    #     return chosen

    # def filter_fn(chosen):
    #     return chosen % 2 == 0

    # def do(elements, *args, **kwargs):
    #     return list(
    #         map(
    #             lambda x: action_fn(x, *args, **kwargs),
    #             filter(lambda y: filter_fn(y, *args, **kwargs), elements),
    #         )
    #     )

    # def do_fast(elements):
    #     return list(map(action_fn, filter(filter_fn, elements)))

    # t0 = time.time()
    # a = do_fast(elements)
    # t1 = time.time()
    # print(t1 - t0)

    # t0 = time.time()
    # b = [action_fn(i) for i in filter(filter_fn, elements)]
    # t1 = time.time()
    # print(t1 - t0)

    # class Value:
    #     def __init__(self, val) -> None:
    #         self.val = val

    # def increment(val: Value):
    #     val.val += 1

    # my_val = Value(0)

    # fn = functools.partial(increment, my_val)
    # fn()
    # fn()
    # print(my_val.val)

    # t0 = time.time()
    # for i in range(10_000):
    #     fn2 = partial(increment, my_val)
    # t1 = time.time()
    # print(t1 - t0)

    # pass

    def preference(a, b) -> int:
        return 1 if a < b else -1 if a > b else 0

    small5 = heapq.nsmallest(5, elements, key=functools.cmp_to_key(preference))

    def filter2(chosen, arg1):
        return chosen % arg1 == 0

    def action2(chosen, arg1):
        return chosen, arg1

    def fastdo2(elements, args):
        return map(
            lambda x: action2(x, args), (y for y in elements if filter2(y, args))
        )

    def fastdo2a(elements, args, action2=action2, filter2=filter2):
        return (action2(x, args) for x in (y for y in elements if filter2(y, args)))

    import timeit

    num = 100

    print(
        timeit.timeit(
            lambda: [action2(i, 2) for i in elements if filter2(i, 2)], number=num
        )
    )

    print(
        timeit.timeit(
            lambda: list(
                map(lambda x: action2(x, 2), filter(lambda y: filter2(y, 2), elements))
            ),
            number=num,
        )
    )

    print(
        timeit.timeit(
            lambda: [action2(i, 2) for i in filter(lambda y: filter2(y, 2), elements)],
            number=num,
        )
    )

    print(
        timeit.timeit(
            lambda: list(
                map(lambda x: action2(x, 2), (y for y in elements if filter2(y, 2)))
            ),
            number=num,
        )
    )

    print(timeit.timeit(lambda: list(fastdo2(elements, 2)), number=num))

    print(timeit.timeit(lambda: list(fastdo2a(elements, 2)), number=num))


def constructor_test():
    import random

    from pycontroller import Controller

    random.seed(0)

    class TestController(Controller):
        counter = 0
        # return_generator = True
        # static_mode = True

        def action(self, chosen: int, arg0, kwarg0=0) -> tuple:
            # self.counter += 1
            return chosen  # , self.counter

        @staticmethod
        def filter(chosen: int, *args) -> bool:
            return chosen % 2 == 0

        @staticmethod
        def preference(a: int, b: int, **kwargs) -> int:
            return -1 if a < b else 1 if a > b else 0

    elements = (random.randint(0, 100000) for _ in range(1000))
    tst = TestController()
    # result = TestController(elements)
    result = tst(elements)
    pass


if __name__ == "__main__":
    # time_tests1()
    # speedtest2()
    constructor_test()
