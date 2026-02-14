from git.remote import flagKeyLiteral


def reverse_iterative(lst: list[int]) -> list[int]:
    """
    Return reversed list. You can use only iteration
    :param lst: input list
    :return: reversed list
    """
    sizeOfList = len(lst)
    answer = [0]*sizeOfList
    for i in range(0, sizeOfList):
        answer[i] = lst[sizeOfList - i - 1]
    return answer


def reverse_inplace_iterative(lst: list[int]) -> None:
    """
    Revert list inplace. You can use only iteration
    :param lst: input list
    :return: None
    """
    sizeOfList = len(lst)
    for i in range(0, int(sizeOfList//2)):
        lst[i], lst[sizeOfList-i-1] = lst[sizeOfList-i-1], lst[i]


def reverse_inplace(lst: list[int]) -> None:
    """
    Revert list inplace with reverse method
    :param lst: input list
    :return: None
    """
    lst.reverse()


def reverse_reversed(lst: list[int]) -> list[int]:
    """
    Revert list with `reversed`
    :param lst: input list
    :return: reversed list
    """
    return list(reversed(lst)) if len(lst)>0 else []


def reverse_slice(lst: list[int]) -> list[int]:
    """
    Revert list with slicing
    :param lst: input list
    :return: reversed list
    """
    return lst[::-1]
