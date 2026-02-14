from string import ascii_lowercase
from math import gcd

def norm(num, den):
    g = gcd(num, den)
    return num // g, den // g

n = int(input())
s = input()

alphabet = ascii_lowercase[:n]
counts = [s.count(c) for c in alphabet]
total = len(s)

print(n)
print(*counts)

pref = [0]
for c in counts:
    pref.append(pref[-1] + c)

intervals = [(pref[i], pref[i+1]) for i in range(n)]
low_num, low_den = 0, 1
high_num, high_den = 1, 1

for ch in s:
    idx = ord(ch) - ord('a')
    a, b = intervals[idx]
    width_num = high_num * low_den - low_num * high_den
    width_den = high_den * low_den
    n_low_num = low_num * (width_den * total) + width_num * a * low_den
    n_low_den = low_den * (width_den * total)
    n_high_num = low_num * (width_den * total) + width_num * b * low_den
    n_high_den = low_den * (width_den * total)
    low_num, low_den = norm(n_low_num, n_low_den)
    high_num, high_den = norm(n_high_num, n_high_den)
q = 1
while True:
    two_q = 1 << q
    p = (low_num * two_q + low_den - 1) // low_den
    if p * high_den < high_num * two_q:
        break
    q += 1
code = bin(p)[2:].zfill(q)
print(code)
