from collections import deque

n: int = int(input())
p: list[int] = list(map(int, input().split()))
p.sort()

q1: deque[int] = deque(p)
q2: deque[int] = deque()

ans: int = 0

def get_min(q1: deque[int], q2: deque[int]) -> int:
    if not q1:
        return q2.popleft()
    if not q2:
        return q1.popleft()

    if q1[0] <= q2[0]:
        return q1.popleft()
    else:
        return q2.popleft()

while len(q1) + len(q2) > 1:
    min_p1: int = get_min(q1, q2)
    min_p2: int = get_min(q1, q2)
    new_node: int = min_p1 + min_p2
    ans += new_node
    q2.append(new_node)

print(ans)
