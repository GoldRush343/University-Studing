def merge_iterative(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    #a:l - m    b:r - n
    n, m = len(lst_a), len(lst_b)
    if n == 0: return lst_b #border case
    if m == 0: return lst_a #border case
    answer = [0]*(n+m)
    l, r = 0, 0
    #doing merge of lists
    for i in range(n+m):
        if l != m and r != n and lst_a[l] <= lst_b[r]: # a <= b -> a
            answer[l + r] = lst_a[l]
            l += 1
        elif r != n:
            answer[l + r] = lst_b[r]
            r += 1
        else:
            answer[l + r] = lst_a[l]
            l += 1
    return answer


def merge_sorted(lst_a: list[int], lst_b: list[int]) -> list[int]:
    """
    Merge two sorted lists in one sorted list using `sorted`
    :param lst_a: first sorted list
    :param lst_b: second sorted list
    :return: merged sorted list
    """
    return sorted(lst_a + lst_b)
