n, m, p = map(int, input().split())
arr: list[int] = list(map(int, input().split()))


class Heap:
    arr: list[int]
    size: int

    def increase_max(self, delta: int) -> None:
        self.arr[0] -= delta
        self.__sift_down(0)

    def top(self) -> int:
        return self.arr[0]

    def __init__(self):
        self.arr = []
        self.size = 0
        self.is_min_heap = False

    def add(self, num: int) -> None:
        self.size += 1
        self.arr.append(num)
        self.__shift_up(self.size - 1)

    def pop(self) -> int:
        val = self.arr[0]
        self.arr[0] = self.arr[self.size - 1]
        self.size -= 1
        self.arr.pop()
        self.__sift_down(0)
        return val

    def __shift_up(self, i: int) -> None:
        while i > 0 and self.arr[i] > self.arr[(i - 1) // 2]:
            self.arr[i], self.arr[(i - 1) // 2] = self.arr[(i - 1) // 2], self.arr[i]
            i = (i - 1) // 2

    def __sift_down(self, i: int) -> None:
        while True:
            l, r = 2 * i + 1, 2 * i + 2
            if l >= self.size:
                break
            mid: int = l
            if r < self.size and self.arr[r] > self.arr[mid]:
                mid = r
            if self.arr[i] >= self.arr[mid]:
                break
            self.arr[i], self.arr[mid] = self.arr[mid], self.arr[i]
            i = mid


heap: Heap = Heap()
for el in arr:
    heap.add(el)

ans: int = 0
for i in range(m):
    if heap.top() > 0:
        ans += min(heap.top(), p)
        heap.increase_max(p)

print(ans)
