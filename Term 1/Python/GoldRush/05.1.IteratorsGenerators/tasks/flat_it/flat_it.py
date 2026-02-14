from collections.abc import Iterable, Iterator
from typing import Any


def flat_it(sequence: Iterable[Any]) -> Iterator[Any]:
    """
    :param sequence: iterable with arbitrary level of nested iterables
    :return: generator producing flatten sequence
    """
    stack = [iter(sequence)]

    while stack:
        try:
            item = next(stack[-1])
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                stack.append(iter(item))
            elif isinstance(item, str):
                for char in item:
                    yield char
            else:
                yield item
        except StopIteration:
            stack.pop()
