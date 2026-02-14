from string import ascii_lowercase

dic: dict[str, int] = {a: i for i, a in enumerate(ascii_lowercase)}
t: str = ""
s: str = input()
ans: list[int] = []
last: int = 25
for c in s:
    tc = t + c
    if tc in dic:
        t += c
    else:
        ans.append(dic[t])
        last += 1
        dic[tc] = last
        t = c
if t != "":
    ans.append(dic[t])
print(*ans)