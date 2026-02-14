n = int(input())
a = list(map(int, input().split()))
a = sorted(a)

# l = 0
cur_l = 0
max_l = 0
# for r in range(n):
#     while l <= r and a[r] - a[l] > 5:
#         max_l = max(r-l, max_l)
#         l += 1
r = 0
for l in range(n):
    while r < n and a[r] - a[l] <= 5:
        r += 1
    max_l = max(max_l, r - l)
print(max_l)
