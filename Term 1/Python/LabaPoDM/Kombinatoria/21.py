n, r = map(int, input().split())
memo = {}


def count(rem:int, min_val:int)->int:
    if rem == 0:
        return 1
    if (rem, min_val) in memo:
        return memo[(rem, min_val)]

    res = 0
    for i in range(min_val, rem + 1):
        res += count(rem - i, i)
    memo[(rem, min_val)] = res
    return res


def rec(n: int, min_val: int, summ: int, k: int)-> None:
    if n == 0:
        print(*summ, sep="+")
        return

    for i in range(min_val, n + 1):
        cnt = count(n - i, i)
        if k < cnt:
            rec(n - i, i, summ + [i], k)
            return
        else:
            k -= cnt

rec(n, 1, [], r)
