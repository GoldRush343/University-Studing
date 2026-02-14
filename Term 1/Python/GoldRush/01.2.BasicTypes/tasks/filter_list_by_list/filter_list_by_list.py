from math import acosh


def filter_list_by_list(lst_a: list[int] | range, lst_b: list[int] | range) -> list[int]:
    """
    Filter first sorted list by other sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: filtered sorted list
    """
    # a:l - m    b:r - n
    n, m = len(lst_a), len(lst_b)
    if n == 0:  # border case
        return []
    if m == 0:  # border case
        return lst_a
    answer = []
    right = 0
    for left in range(n):
        if right != n and lst_a[left] < lst_b[right]:
            answer.append(lst_a[left])
            continue
        while right != n and lst_a[left] > lst_b[right]:
            right += 1
        if right == n or lst_a[left] != lst_b[right]:
            answer.append(lst_a[left])
    return answer
