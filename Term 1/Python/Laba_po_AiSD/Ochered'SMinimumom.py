class QueueWithMin:
    def __init__(self):
        self._in: list[tuple[int, int]] = []
        self._out: list[tuple[int, int]] = []

    def push(self, value: int) -> None:
        if not self._in:
            self._in.append((value, value))
        else:
            self._in.append((value, min(value, self._in[-1][1])))

    def pop(self) -> None:
        if not self._out:
            while self._in:
                v: int = self._in.pop()[0]
                minn: int = v if not self._out else min(v, self._out[-1][1])
                self._out.append((v, minn))
        if self._out:
            self._out.pop()

    def min(self) -> int:
        if not self._out and not self._in:
            return -1
        elif not self._out:
            return self._in[-1][1]
        elif not self._in:
            return self._out[-1][1]
        else:
            return min(self._in[-1][1], self._out[-1][1])


my_stack = QueueWithMin()
qs: int = int(input())
for _ in range(qs):
    cur = input()
    match cur:
        case "pop":
            my_stack.pop()
        case "min?":
            print(my_stack.min())
        case _:
            _, value = cur.split()
            my_stack.push(int(value))
