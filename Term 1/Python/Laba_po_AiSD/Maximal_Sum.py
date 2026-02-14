n: int = int(input())
a: list = list(map(int, input().split()))

sum_ = 0
min_sum = 0
min_pos = -1

max_sum = a[0]
ans_l = 0
ans_r = 0

for r in range(n):
    sum_ += a[r]
    cur_sum = sum_ - min_sum
    if cur_sum > max_sum:
        max_sum = cur_sum
        ans_l = min_pos + 1
        ans_r = r
    if sum_ < min_sum:
        min_sum = sum_
        min_pos = r
print(max_sum)
print(ans_l + 1, ans_r + 1)