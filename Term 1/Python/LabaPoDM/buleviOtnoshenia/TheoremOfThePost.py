def isT0(ti, argSize):
    return not ti[0]
def isT1(ti, argSize):
    return ti[-1]
def isTs(ti, argSize):
    if argSize == 0: return False
    n = len(ti)
    for i in range(n//2):
        if ti[i] == ti[n-i-1]:
            return False
    return True
def isTm(ti, argSize):
    n = len(ti)
    for vec in range(n):
        for i in range(argSize):
            if (vec >> i) & 1 == 0:
                vecTo1 = vec | (1 << i)
                if ti[vec] > ti[vecTo1]:
                    return False
    return True
def isTl(ti, argSize):
    n = len(ti)
    pzh = ti[:]
    for i in range(argSize):
        for vec in range(n):
            if (vec & (1 << i)):
                pzh[vec] ^= pzh[vec ^ (1 << i)]
    for vec in range(n):
        if bin(vec).count('1') >= 2 and pzh[vec] == 1:
            return False
    return True
Post = [isT0, isT1, isTs, isTm, isTl]
cnt = int(input())
funcs = []
argSizes = [0]*cnt
for i in range(cnt):
    argSizes[i], tmp = input().split()
    funcs.append(list(map(int, tmp)))
res = [0]*5 #  где мы не находимся
argSizes = list(map(int, argSizes))
for k in range(len(funcs)):
    f = funcs[k]
    for i in range(5):
        cond = Post[i]
        if not cond(f, argSizes[k]):
            res[i] = 1
print("YES" if all(res) else "NO")