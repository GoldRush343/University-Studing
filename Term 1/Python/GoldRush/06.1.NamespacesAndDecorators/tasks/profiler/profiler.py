import functools
from datetime import datetime


def profiler(func):
    """
    Returns profiling decorator, which counts calls of function
    and measure last function execution time.
    Results are stored as function attributes: `calls`, `last_time_taken`
    :param func: function to decorate
    :return: decorator, which wraps any function passed
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        is_top_level = wrapper.rec_depth == 0

        if is_top_level:
            wrapper.calls = 0
            wrapper.start_time = datetime.now()

        wrapper.rec_depth += 1
        wrapper.calls += 1

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            wrapper.rec_depth -= 1
            if is_top_level:
                delta = datetime.now() - wrapper.start_time
                wrapper.last_time_taken = delta.total_seconds()

    wrapper.rec_depth = 0
    wrapper.calls = 0
    wrapper.last_time_taken = 0.0

    return wrapper
