import functools
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TypeVar

Function = TypeVar('Function', bound=Callable[..., Any])


def cache(max_size: int) -> Callable[[Function], Function]:
    """
    Returns decorator, which stores result of function
    for `max_size` most recent function arguments.
    :param max_size: max amount of unique arguments to store values for
    :return: decorator, which wraps any function passed
    """

    def decorator(func: Function) -> Function:
        _cache: OrderedDict = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))

            if key in _cache:
                _cache.move_to_end(key)
                return _cache[key]

            result = func(*args, **kwargs)

            _cache[key] = result

            if len(_cache) > max_size:
                _cache.popitem(last=False)

            return result

        return wrapper  # type: ignore

    return decorator
