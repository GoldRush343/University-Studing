def product_(*args, repeat):
    elems = [tuple(pool) for pool in args] * repeat
    n = len(elems)
    answer = [0] * n
    yield tuple(elems[i][0] for i in range(n))
    while True:
        for i in range(n - 1, -1, -1):
            if answer[i] + 1 < len(elems[i]):
                answer[i] += 1
                yield tuple(elems[x][answer[x]] for x in range(n))
                break
            else:
                answer[i] = 0
        else:
            return

n: int = int(input())
pr = product_(range(2), repeat=n)
print(*("".join(map(str, x)) for x in pr), sep="\n")
