from string import ascii_lowercase
from math import gcd

def get(num, den):
    g = gcd(num, den)
    return num // g, den // g

n = int(input())
counts = list(map(int, input().split()))
code = input()
alphabet = ascii_lowercase[:n]
total = sum(counts)
pref = [0]
for c in counts:
    pref.append(pref[-1] + c)
q = len(code)
p = int(code, 2)
two_q = 1 << q
low, low_den = 0, 1
high, high_den = 1, 1

result = []
for _ in range(total):
    w = high * low_den - low * high_den
    w_den = high_den * low_den
    for i in range(n):
        a = pref[i]
        b = pref[i+1]
        l = low * (w_den * total) + w * a * low_den
        l_den = low_den * (w_den * total)
        r = low * (w_den * total) + w * b * low_den
        r_den = low_den * (w_den * total)

        if l * two_q <= p * l_den and p * r_den < r * two_q:
            result.append(alphabet[i])
            low, low_den = get(l, l_den)
            high, high_den = get(r, r_den)
            break
print("".join(result))
