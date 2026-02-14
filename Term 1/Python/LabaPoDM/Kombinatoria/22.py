parts = list(map(int, input().split('+')))
n = sum(parts)
memo = {}


def count(rem: int, min_val: int) -> int:
    if rem == 0:
        return 1
    if (rem, min_val) in memo:
        return memo[(rem, min_val)]

    res = 0
    for i in range(min_val, rem + 1):
        res += count(rem - i, i)
    memo[(rem, min_val)] = res
    return res


rank = 0
min_val = 1
cur_n = n

for x in parts:
    for i in range(min_val, x):
        rank += count(cur_n - i, i)

    cur_n -= x
    min_val = x

print(rank)
