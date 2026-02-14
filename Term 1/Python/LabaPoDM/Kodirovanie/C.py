def step():
    for i in range(len(s)):
        mat[i] = s[i] + mat[i]
    mat.sort()

s: str = input()
mat: list[str] = ["" for _ in range(len(s))]
for i in range(len(s)):
    step()
print(mat[0])
