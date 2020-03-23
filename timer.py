"""a timer decorator for timing functions."""

from functools import wraps
from statistics import mean, stdev
import sys
import time


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def timer(func):
    """timer decorator.
    usage:
    >>> @timer
    >>> def function_to_be_timed():
    >>>     pass
    """
    @wraps(func)
    def time_func(*args, **kwargs):
        """wrapper for func to be timed."""
        i = 0
        tt = []
        eprint(f"timing func:: {func.__name__}")
        while i < 4:
            init_t = time.perf_counter()
            res = func(*args, **kwargs)
            final_t = time.perf_counter()
            tt.append(final_t - init_t)
            i += 1
        eprint(f"mean: {mean(tt):10.4f}, std: {stdev(tt):10.4f} sec.")
        return res
    return time_func
