n = int(input())

def rec(n, min_val, summ):
    if n == 0:
        print(*summ, sep="+")
        return

    for i in range(min_val, n + 1):
        rec(n - i, i, summ + [i])

rec(n, 1, [])
