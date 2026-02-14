n: int = int(input())
if n == 1:
    print("0\n1")
    exit()

bul: int = 1 << n
visited: list[bool] = [False] * bul

cur: int = 0
visited[0] = True

result: list[int] = [0] * bul
result[0] = 0
count: int = 1

mask: int = (1 << (n - 1)) - 1
for i in range(1, bul):
    pref = (cur & mask) << 1
    cand_1 = pref | 1
    if not visited[cand_1]:
        visited[cand_1] = True
        cur = cand_1
    else:
        cand_0 = pref
        visited[cand_0] = True
        cur = cand_0
    result[i] = cur

print(*[f'{x:0{n}b}' for x in result] ,sep='\n')
