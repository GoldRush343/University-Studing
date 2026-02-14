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
                dp[i][j] += 2 * dp[i + 1][j + 1]

        if j > 0:
            dp[i][j] += dp[i + 1][j - 1]

result = []
stack = []
cur_depth = 0
cur = k

for i in range(2 * n):
    used_opens = (i + cur_depth) // 2

    if used_opens < n:
        count = dp[i + 1][cur_depth + 1]
        if cur < count:
            result.append('(')
            stack.append('(')
            cur_depth += 1
            continue
        cur -= count

    if cur_depth > 0 and stack and stack[-1] == '(':
        count = dp[i + 1][cur_depth - 1]
        if cur < count:
            result.append(')')
            stack.pop()
            cur_depth -= 1
            continue
        cur -= count

    if used_opens < n:
        count = dp[i + 1][cur_depth + 1]
        if cur < count:
            result.append('[')
            stack.append('[')
            cur_depth += 1
            continue
        cur -= count

    result.append(']')
    stack.pop()
    cur_depth -= 1

print(''.join(result))