from math import factorial


def C(n, k):
    if k < 0 or k > n: return 0
    return factorial(n) // (factorial(k) * factorial(n - k))


def get_combination(n: int, k: int, m: int) -> list[int]:
    answer = []
    cur_num = 1

    while k > 0:
        others = n - cur_num
        if others >= k - 1:
            count = C(others, k - 1)
        else:
            count = 0
        if m < count:
            answer.append(cur_num)
            k -= 1
        else:
            m -= count
        cur_num += 1

    return answer

n, k, m = map(int, input().split())
print(*get_combination(n, k, m))
