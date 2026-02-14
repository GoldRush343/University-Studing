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


n, k = map(int, input().split())

for i in combination([i for i in range(1,n+1)],k):
    print(*i)
