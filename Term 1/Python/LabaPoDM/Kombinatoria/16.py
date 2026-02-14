n, k = map(int, input().split())

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

result = []
cur_depth = 0
cur = k

for i in range(2 * n):
    used_opens = (i + cur_depth) // 2
    can_place_open = False
    count_with_open = 0
    if used_opens < n and cur_depth + 1 <= n:
        count_with_open = dp[i + 1][cur_depth + 1]
        can_place_open = True

    if can_place_open and cur < count_with_open:
        result.append('(')
        cur_depth += 1
    else:
        result.append(')')
        if can_place_open:
            cur -= count_with_open
        cur_depth -= 1

print(''.join(result))
