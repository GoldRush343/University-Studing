from collections.abc import Iterable, Iterator, Sized


class RangeIterator(Iterator[int]):
    """The iterator class for Range"""
    def __init__(self, range_: 'Range') -> None:
        self.start = range_.start
        self.stop = range_.stop
        self.step = range_.step
        self.cur = self.start - self.step

    def __iter__(self) -> 'RangeIterator':
        return self

    def __next__(self) -> int:
        self.cur += self.step
        if (self.step < 0 and self.cur <= self.stop) or (self.step > 0 and self.cur >= self.stop):
            raise StopIteration()
        return self.cur


class Range(Sized, Iterable[int]):
    """The range-like type, which represents an immutable sequence of numbers"""
    start: int = 0
    stop: int = 0
    step: int = 0

    def __init__(self, *args: int) -> None:
        """
        :param args: either it's a single `stop` argument
            or sequence of `start, stop[, step]` arguments.
        If the `step` argument is omitted, it defaults to 1.
        If the `start` argument is omitted, it defaults to 0.
        If `step` is zero, ValueError is raised.
        """
        if len(args) == 1:
            self.start = 0
            self.stop = args[0]
            self.step = 1
        elif len(args) == 2:
            self.start = args[0]
            self.stop = args[1]
            self.step = 1
        elif len(args) == 3:
            self.start = args[0]
            self.stop = args[1]
            self.step = args[2]
            if self.step == 0:
                raise ValueError("range step must not be zero")
        else:
            raise TypeError("range expected at most 3 arguments")

    def __iter__(self) -> 'RangeIterator':
        return RangeIterator(self)

    def __repr__(self) -> str:
        if self.step == 1:
            return f"range({self.start}, {self.stop})"
        return f"range({self.start}, {self.stop}, {self.step})"

    def __str__(self) -> str:
        return self.__repr__()

    def __contains__(self, key: int) -> bool:
        if self.step > 0:
            return self.start <= key < self.stop and (key - self.start) % self.step == 0
        else:
            return self.stop < key <= self.start and (key - self.start) % self.step == 0

    def __getitem__(self, key: int) -> int:
        if key < 0:
            key += len(self)
        if not 0 <= key < len(self):
            raise IndexError("range index out of range")
        return self.start + key * self.step

    def __len__(self) -> int:
        if self.step > 0:
            return max(0, (self.stop - self.start + self.step - 1) // self.step)
        else:
            return max(0, (self.start - self.stop - self.step - 1) // (-self.step))
