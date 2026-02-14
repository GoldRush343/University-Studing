class queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def push(self, value: int) -> None:
        new= Node(value)
        self.size += 1
        if self.tail is None:
            self.head = self.tail = new
        else:
            new.prev = self.tail
            self.tail.next = new
            self.tail = new

    def pop(self) -> int:
        res = self.head.value
        self.size -= 1
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
        return res

    def front(self) -> int:
        return self.head.value

    def size(self) -> int:
        return self.size

    def clear(self) -> None:
        self.head = None
        self.tail = None
        self.size = 0


class Node:
    def __init__(self, value, next=None, prev=None):
        self.value = value
        self.next = next
        self.prev = prev


my_stack = queue()
while (cur := input()) != "exit":
    match cur:
        case "front":
            print(my_stack.front())
        case "pop":
            print(my_stack.pop())
        case "size":
            print(my_stack.size)
        case "clear":
            my_stack.clear()
            print("ok")
        case _:
            _, value = cur.split()
            my_stack.push(int(value))
            print("ok")
print("bye")
