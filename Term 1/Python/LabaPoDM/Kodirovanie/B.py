from itertools import cycle, islice

s: str = input()
a = [list(islice(cycle(s), i, i + len(s))) for i in range(len(s))]
a.sort()
ans: str = ""
for el in a:
    ans += el[-1]
print(ans)