n, k = map(int, input().split())

grey_codes = [""]

for i in range(n):
    new = []
    for j in range(k):
        cur = str(j)
        if j % 2 == 0:
            for code in grey_codes:
                new.append(cur + code)
        else:
            for code in reversed(grey_codes):
                new.append(cur + code)
    grey_codes = new

print(*grey_codes, sep="\n")
