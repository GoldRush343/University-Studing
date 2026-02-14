n = int(input())

def backtrack(s, left, right):
    global n
    if len(s) == 2 * n:
        print(s)
        return
    if left < n:
        backtrack(s + '(', left + 1, right)
    if right < left:
        backtrack(s + ')', left, right + 1)

backtrack("", 0, 0)
