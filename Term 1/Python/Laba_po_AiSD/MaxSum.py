n: int = int(input())
arr: list[int] = list(map(int, input().split()))

prev: list[int] = [0]*(n+1)
s: int = 0
for i in range(n):
    prev[i+1] = s + arr[i]
    s += arr[i]

min_l: int = 0
max_sum: int = -1_000_000_000
for r in range(1, n+1):
    if prev[r] - prev[min_l] > max_sum:
        max_sum = prev[r] - prev[min_l]
    if prev[r] < prev[min_l]:
        min_l = r
print(max_sum)