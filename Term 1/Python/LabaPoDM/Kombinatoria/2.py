n = int(input())
for i in range(1 << n):
    g = i ^ (i // 2)
    print(format(g, '0{}b'.format(n)))