import typing as tp
from math import factorial

def rec(elements: tp.List[int], k: int) -> tp.List[int]:
    if not elements:
        return []
    n = len(elements)
    block_size = factorial(n - 1)
    index = k // block_size
    cur = elements[index]
    others = elements[:index] + elements[index + 1:]
    new_k = k % block_size
    return [cur] + rec(others, new_k)

n, k = map(int, input().split())
print(*rec([i for i in range(1, n+1)], k))
