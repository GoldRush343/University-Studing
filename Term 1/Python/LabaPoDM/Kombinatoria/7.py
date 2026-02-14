def permutations_(elements):
    if len(elements) <= 1:
        yield elements
        return

    for i in range(len(elements)):
        cur = elements[i]
        others = elements[:i] + elements[i+1:]
        for p in permutations_(others):
            yield [cur] + p

n = int(input())
for t in permutations_([i for i in range(1,n+1)]):
    print(*t)
