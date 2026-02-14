class Node:
    def __init__(self, value, next=None, prev=None):
        self.value = value
        self.next = next
        self.prev = prev


class deque:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def push_back(self, value: int):
        new = Node(value)
        self.size += 1
        if self.tail is None:
            self.head = self.tail = new
        else:
            new.prev = self.tail
            self.tail.next = new
            self.tail = new

    def push_front(self, value: int) -> None:
        new = Node(value)
        self.size += 1
        if self.tail is None:
            self.head = self.tail = new
        else:
            new.next = self.head
            self.head.prev = new
            self.head = new

    def pop_front(self):
        if self.head is None:
            return
        self.size -= 1
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None

    def pop_back(self):
        if self.tail is None:
            return
        self.size -= 1
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None

    def front(self):
        return self.head.value

    def back(self):
        return self.tail.value

    def get_size(self):
        return self.size


n = int(input())
k = int(input())
arr = [int(input()) for _ in range(n)]

deq = deque()

for i in range(n):
    while deq.get_size() > 0 and arr[deq.back()] >= arr[i]:
        deq.pop_back()

    deq.push_back(i)
    if deq.front() + k <= i:
        deq.pop_front()

    if i >= k - 1:
        print(arr[deq.front()], end=' ')
