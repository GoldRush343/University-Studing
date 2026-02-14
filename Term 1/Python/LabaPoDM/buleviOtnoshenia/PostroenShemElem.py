n = int(input())
Pn = (1 << n)
ans = {}
form = [''] * Pn
ti = [0] * Pn
cntOfElems = n

def add(oper, args):
    global cntOfElems
    elem = (oper, tuple(args))
    for k, v in ans.items():
        if v == elem:
            return k
    cntOfElems += 1
    ans[cntOfElems] = elem
    return cntOfElems

for i in range(Pn):
    form[i], ti[i] = input().split()
ti = list(map(int, ti))

if all(ti):
    otrs = [add(1, [1])]
    final = add(3, [1, otrs[0]])
elif not any(ti):
    otrs = [add(1, [1])]
    final = add(2, [1, otrs[0]])
else:
    otrs = [add(1, [i + 1]) for i in range(n)]

    def getConuct(s: str) -> int:
        elems = []
        for i, c in enumerate(s):
            if c == '0':
                elems.append(otrs[i])
            elif c == '1':
                elems.append(i + 1)
        if len(elems) == 1:
            return elems[0]
        cur = add(2, [elems[0], elems[1]])
        for e in elems[2:]:
            cur = add(2, [cur, e])
        return cur

    cons = [getConuct(form[i]) for i in range(Pn) if ti[i]]

    if len(cons) == 1:
        final = add(3, [cons[0], cons[0]])
    else:
        cur = add(3, [cons[0], cons[1]])
        for c in cons[2:]:
            cur = add(3, [cur, c])
        final = cur

print(cntOfElems)
for op, args in ans.values():
    print(op, *args)
