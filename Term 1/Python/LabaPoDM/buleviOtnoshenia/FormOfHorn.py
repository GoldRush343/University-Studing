n, k = map(int, input().split())
mat = [list(map(int, input().split())) for _ in range(k)]
values = [-1] * n


def simplify():
    newMat = []
    for row in mat:
        clauseTrue = False
        newRow = []
        for i in range(n):
            x = row[i]
            if x == -1:
                newRow.append(-1)
                continue
            if values[i] == -1:
                newRow.append(x)
                continue
            if x == 1 and values[i] == 1:
                clauseTrue = True
                break
            if x == 0 and values[i] == 0:
                clauseTrue = True
                break
            newRow.append(-1)
        if not clauseTrue:
            newMat.append(newRow)
    return newMat


def findSingle(m):
    for row in m:
        lits = [(i, v) for i, v in enumerate(row) if v != -1]
        if len(lits) == 1:
            i, v = lits[0]
            if v == 1:
                return i, 1
            if v == 0:
                return i, 0
    return None


def isSkobeZero(m):
    for row in m:
        if all(x == -1 for x in row):
            return True
    return False


def isZero():
    global mat
    while True:
        if isSkobeZero(mat):
            return True
        single = findSingle(mat)
        if single is None:
            return False
        i, val = single
        if values[i] != -1 and values[i] != val:
            return True
        values[i] = val
        mat = simplify()


print("YES" if isZero() else "NO")
