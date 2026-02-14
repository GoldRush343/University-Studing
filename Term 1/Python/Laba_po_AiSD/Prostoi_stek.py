class stack:
    def __init__(self):
        self.last = None
        self.size = 0

    def push(self, value: int) -> None:
        self.size += 1
        self.last = Node(value, self.last)

    def back(self):
        return self.last.value

    def pop(self):
        self.size -= 1
        res = self.last.value
        tmp = self.last.next
        del self.last
        self.last = tmp
        return res

    def size(self):
        return self.size

    def clear(self):
        self.last = None
        self.size = 0


class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next


my_stack = stack()
while (cur := input()) != "exit":
    match cur:
        case "back":
            print(my_stack.back())
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
