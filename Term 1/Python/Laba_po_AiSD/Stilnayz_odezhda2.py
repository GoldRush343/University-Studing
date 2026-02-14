import heapq


def get_sum_diff(best: list[int]) -> int:
    return max(best) - min(best)


matrix = []
for i in range(4):
    n = int(input())
    matrix.append(sorted(map(int, input().split())))

heap: list = []
best: list[int] = [-1] * 4

for i, arr in enumerate(matrix):
    heapq.heappush(heap, (arr[0], i))
    best[i] = arr[0]

pointers = [0] * 4
new_best = best.copy()

while heap:
    last, ind = heapq.heappop(heap)
    pointers[ind] += 1
    if pointers[ind] < len(matrix[ind]):
        heapq.heappush(heap, (matrix[ind][pointers[ind]], ind))
    else:
        continue
    new_best[ind] = matrix[ind][pointers[ind]]
    if get_sum_diff(new_best) < get_sum_diff(best):
        best = new_best.copy()

print(*best)
