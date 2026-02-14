n = int(input())
up = list(map(int, input().split()))
m = int(input())
down = list(map(int, input().split()))
l, r = 0, 0
ans_up, ans_down = 0, 1e9
while l < n and r < m:
    if abs(up[l] - down[r]) < abs(ans_down - ans_up):
        ans_up = up[l]
        ans_down = down[r]
    if r == m-1 or up[l] <= down[r]:
        l += 1
    elif l == n-1 or up[l] > down[r]:
        r += 1
print(ans_up, ans_down)
