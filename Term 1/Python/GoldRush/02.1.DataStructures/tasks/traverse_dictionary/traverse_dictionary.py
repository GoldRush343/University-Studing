import typing as tp


def traverse_dictionary_immutable(
        dct: tp.Mapping[str, tp.Any],
        prefix: str = "") -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :param prefix: prefix for key used for passing total path through recursion
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    res = list()
    for key, value in dct.items():
        if isinstance(value, dict):
            tdi = traverse_dictionary_immutable(value, f'{prefix}{key}.')
            for key1, value1 in tdi:
                res.append((f'{key1}', value1))
        else:
            res.append((f'{prefix}{key}', value))
    return res


def traverse_dictionary_mutable(
        dct: tp.Mapping[str, tp.Any],
        result: list[tuple[str, int]],
        prefix: str = "") -> None:
    """
    :param result: list with pairs: (full key from root to leaf joined by ".", value)
    :param prefix: prefix for key used for passing total path through recursion
    :return: None
    """
    for key, value in dct.items():
        if isinstance(value, dict):
            traverse_dictionary_mutable(value, result, f'{prefix}{key}.')
        else:
            result.append((f'{prefix}{key}', value))


def traverse_dictionary_iterative(
        dct: tp.Mapping[str, tp.Any]
        ) -> list[tuple[str, int]]:
    """
    :param dct: dictionary of undefined depth with integers or other dicts as leaves with same properties
    :return: list with pairs: (full key from root to leaf joined by ".", value)
    """
    result = []
    stack = list(dct.items())
    while stack:
        key, value = stack[-1]
        if isinstance(value, dict):
            new_dict = dict(value)
            stack.pop()
            for key1, value1 in new_dict.items():
                stack.append((f'{key}.{key1}', value1))
        else:
            result.append((key, value))
            stack.pop()
    return result

