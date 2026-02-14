n, k = map(int, input().split())
places = list(map(int, input().split()))

l = 0
cur_sum = 0
ans_l = -1
ans_r = 1e9
min_len = n + 1

for r in range(n):
    cur_sum += places[r]
    while cur_sum >= k and l <= r:
        if cur_sum == k and r - l < ans_r - ans_l:
            ans_l = l + 1
            ans_r = r + 1
        cur_sum -= places[l]
        l += 1

if ans_l != -1:
    print(ans_l, ans_r)
else:
    print(-1)
