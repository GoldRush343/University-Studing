import typing as tp
from typing import Generator

def combination(elements, k):
    n = len(elements)
    if n == k:
        yield elements
        return
    if k == 0:
        yield []
        return
    for i in range(n):
        cur = elements[i]
        others = elements[i+1:]
        iterator = combination(others, k-1)
        for com in iterator:
            yield [cur] + com


def rec(elements: tp.List[int], k: int) -> Generator[list[list[int]], None, None]:
    n = len(elements)
    if k == 1:
        yield [elements]
        return
    if k == n:
        yield [[x] for x in elements]
        return

    first = elements[0]
    not_first = elements[1:]
    for i in range(n - k + 1):
        for com in combination(not_first, i):
            cur = [first] + list(com)
            others = [x for x in not_first if x not in com]
            for tail in rec(others, k - 1):
                yield [cur] + tail


n, k = map(int, input().split())
for cur in rec([i for i in range(1, n + 1)], k):
    for el in cur:
        print(*el)
    print()
