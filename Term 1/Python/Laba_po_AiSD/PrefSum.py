n: int = int(input())
arr: list[int] = list(map(int, input().split()))

prev: list[int] = [0]*(n+1)
s: int = 0
for i in range(n):
    prev[i+1] = s + arr[i]
    s += arr[i]

qs: int = int(input())
for _ in range(qs):
    l, r = map(int, input().split())
    r -= 1
    l -= 1
    print(prev[r+1] - prev[l])