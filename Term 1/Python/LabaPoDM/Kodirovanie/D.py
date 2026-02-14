from string import ascii_lowercase

alpha: list[str] = list(ascii_lowercase)
s: str = input()
ans: list[int] = []
for ch in s:
    ind = alpha.index(ch)
    ans.append(ind+1)
    alpha.pop(ind)
    alpha.insert(0,ch)
print(*ans)