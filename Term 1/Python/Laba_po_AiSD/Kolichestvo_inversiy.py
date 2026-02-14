n: int = int(input())
arr: list[int] = list(map(int, input().split()))
cnt: int = 0


def merge(a: list[int], b: list[int]) -> list[int]:
    global cnt
    """
    :param a: left sorted array
    :param b: right sorted array
    :return: one sorted array
    """
    i, j = 0, 0
    c = []
    while i < len(a) or j < len(b):
        if i == len(a):
            c.append(b[j])
            j += 1
        elif j == len(b) or a[i] <= b[j]:
            c.append(a[i])
            i += 1
        else:
            c.append(b[j])
            cnt += len(a) - i
            j += 1
    return c


def merge_sort(a: list[int], l: int, r: int) -> list[int]:
    """
    :return: sorted list
    """
    if l + 1 == r:
        return [a[l]]
    m: int = l + (r - l) // 2
    left = merge_sort(a, l, m)
    right = merge_sort(a, m, r)
    return merge(left, right)

merge_sort(arr, 0, len(arr))
print(cnt)