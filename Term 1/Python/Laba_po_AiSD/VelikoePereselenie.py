n: int = int(input())
arr: list = list(map(int, input().split()))
stack: list[int] = []

ans: list[int] = [0]*n

for i in range(n-1, -1, -1):
    if not stack:
        ans[i] = -1
    else:
        while stack and arr[i] <= arr[stack[-1]]:
            stack.pop()
        if not stack:
            ans[i] = -1
        else:
            ans[i] = stack[-1]
    stack.append(i)

print(*ans)