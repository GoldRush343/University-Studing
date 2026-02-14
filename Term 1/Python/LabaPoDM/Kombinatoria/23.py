s = input()
n = len(s)

i = n - 1
while i >= 0 and s[i] == '0':
    i -= 1
if i == -1:
    print('-')
else:
    print(s[:i] + '0' + '1' * (n - 1 - i))

i = n - 1
while i >= 0 and s[i] == '1':
    i -= 1

if i == -1:
    print('-')
else:
    print(s[:i] + '1' + '0' * (n - 1 - i))
