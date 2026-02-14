s = input()
n = len(s) // 2

dp = [[0] * (n + 2) for _ in range(2 * n + 2)]
dp[2 * n][0] = 1

for i in range(2 * n - 1, -1, -1):
    for j in range(n + 1):
        if (i + j) % 2 != 0:
            continue

        used_opens = (i + j) // 2
        if used_opens < n:
            if j + 1 <= n:
                dp[i][j] += dp[i + 1][j + 1]
        if j > 0:
            dp[i][j] += dp[i + 1][j - 1]

k = 0
cur_depth = 0

for i in range(2 * n):
    used_opens = (i + cur_depth) // 2
    can_place_open = False
    count_with_open = 0
    if used_opens < n and cur_depth + 1 <= n:
        count_with_open = dp[i + 1][cur_depth + 1]
        can_place_open = True

    if s[i] == '(':
        cur_depth += 1
    else:
        if can_place_open:
            k += count_with_open
        cur_depth -= 1

print(k)