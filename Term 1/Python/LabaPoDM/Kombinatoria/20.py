s: str = input()
n: int = len(s) // 2

dp = [[0] * (n + 2) for _ in range(2 * n + 2)]
dp[2 * n][0] = 1

for i in range(2 * n - 1, -1, -1):
    for j in range(n + 1):
        if (i + j) % 2 != 0:
            continue

        used_opens = (i + j) // 2
        if used_opens < n and j + 1 <= n:
            dp[i][j] += 2 * dp[i + 1][j + 1]

        if j > 0:
            dp[i][j] += dp[i + 1][j - 1]

k = 0
cur_depth = 0
stack = []

for i in range(2*n):
    used_opens = (i + cur_depth) // 2

    if used_opens < n:
        if s[i] == '(':
            stack.append('(')
            cur_depth += 1
            continue
        else:
            k += dp[i + 1][cur_depth + 1]

    if cur_depth > 0 and stack and stack[-1] == '(':
        if s[i] == ')':
            stack.pop()
            cur_depth -= 1
            continue
        else:
            k += dp[i + 1][cur_depth - 1]

    if used_opens < n:
        if s[i] == '[':
            stack.append('[')
            cur_depth += 1
            continue
        else:
            k += dp[i + 1][cur_depth + 1]

    if s[i] == ']':
        stack.pop()
        cur_depth -= 1
        continue

print(k)
