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
pr = product_('01', repeat=n)
cnt = 0
result = []
for v in pr:
    cur = ''.join(v)
    if '11' not in cur:
        result.append(cur)
        cnt += 1

print(cnt)
print(*result,sep='\n')
