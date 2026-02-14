n = int(input())
PowN = (1 << n)
ti = [0] * PowN
form = [0] * PowN
for i in range(PowN):
    form[i], ti[i] = input().split()
ti = list(map(int, ti))

for i in range(n):
    for vec in range(PowN):
        if (vec & (1 << i)):
            ti[vec] ^= ti[vec ^ (1 << i)]

for i in range(PowN):
    print(f'{form[i]} {ti[i]}')