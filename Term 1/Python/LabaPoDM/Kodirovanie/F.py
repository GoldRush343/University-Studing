from string import ascii_lowercase

n = int(input())
codes = list(map(int, input().split()))

dic = {i: c for i, c in enumerate(ascii_lowercase)}
next_code = 26

X = codes[0]
t = dic[X]
result = t

for Y in codes[1:]:
    if Y in dic:
        cur = dic[Y]
    else:
        cur = t + t[0]

    result += cur
    dic[next_code] = t + cur[0]
    next_code += 1
    t = cur

print(result)
