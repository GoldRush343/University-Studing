n = int(input())

def getF(n: int) -> str:
    if n == 1:
        return "((A0|B0)|(A0|B0))"
    An_or_Bn = f'((A{n-1}|A{n-1})|(B{n-1}|B{n-1}))'
    Cha = getF(n-1)
    return f'(({Cha}|{An_or_Bn})|(A{n-1}|B{n-1}))'

print(getF(n))
