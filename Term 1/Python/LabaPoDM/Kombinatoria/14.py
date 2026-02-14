from math import factorial

n: int = int(input())
per = list(map(int, input().split()))


def get_permutation_rank(n: int, per: int) -> int:
    available = list(range(1, n + 1))
    ans = 0

    for i in range(n):
        val = per[i]
        idx = available.index(val)
        suffix_len = n - 1 - i
        fact = factorial(suffix_len)
        ans += idx * fact
        available.pop(idx)
    return ans


print(get_permutation_rank(n, per))
