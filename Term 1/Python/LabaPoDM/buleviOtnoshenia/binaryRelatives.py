n = int(input())
R = [[0] for i in range(n)]
S = [[0] for j in range(n)]
for i in range(n):
    R[i] = list(map(int, input().split()))
for i in range(n):
    S[i] = list(map(int, input().split()))

def isRef(s):
    for i in range(n):
        if s[i][i] != 1:
            return False
    return True

def isNotRef(s):
    for i in range(n):
        if s[i][i] == 1:
            return False
    return True

def isSym(s):
    for i in range(n):
        for j in range(n):
            if s[i][j] != s[j][i]:
                return False
    return True

def isAntiSym(s):
    for i in range(n):
        for j in range(n):
            if s[i][j] == s[j][i] == 1 and i != j:
                return False
    return True

def isTran(s):
    res = True
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if s[i][j] and s[j][k] and not s[i][k]:
                    res = False
    return res

opers = [isRef, isNotRef, isSym, isAntiSym, isTran]
for oper in opers:
    print(int(oper(R)), end=" ")
print()
for oper in opers:
    print(int(oper(S)), end=" ")
print()

Res = [[0]*n for j in range(n)]
for i in range(n):
    for j in range(n):
        for k in range(n):
            if R[i][j] and S[j][k]:
                Res[i][k] = 1
for i in range(n):
    print(*Res[i])
