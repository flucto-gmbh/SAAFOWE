from pyclbr import Function
from typing import Callable, Iterable


def partition(it : Iterable, eq : Function) -> Iterable:
    '''
    Generate a partition of iterable it, using equivalence function eq.

    # Inputs

    it may be any
    [iterable](https://docs.python.org/3/glossary.html#term-iterable), e.g.
    a list, a generator, etc.

    eq is a function that takes two arguments a, b and returns True if a and b
    are equivalent, and False otherwise. For example
        eq = lambda a, b: (a // 10) == (b // 10)
    returns True iff numbers a, b are equal when rounded to the second digit.

    # Outputs

    The generated values are themselves generators (aka "inner" generators), so
    that iterables of arbitrary length (even infinite length) can be consumed.
    The inner generators are maximum sequences of equivalent elements of the
    given iterable it. For example, if
        it = (8, 9, 10, 11, 19, 20, 21)
    and eq as above, then the generated values are (in tuple notation):
        (8, 9), (10, 11, 19), (20, 21).
    '''
    it = iter(it)
    global start
    try:
        start = next(it)
    except StopIteration:
        raise
    def inner():
        global start
        x = start
        yield x
        while True:
            try:
                y = next(it)
            except StopIteration:
                start = None
                raise
            if eq(x, y):
                yield y
                x = y
            else:
                start = y
                break
    while start is not None:
        yield inner()

def partition_test():
    it = range(30)
    eq = lambda a, b: (a // 10) == (b // 10)
    for g in partition(it, eq):
        print(', '.join(map(str, g)))
    it = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    for g in partition(it, eq):
        print(', '.join(map(str, g)))

if __name__ == '__main__':
    partition_test()
