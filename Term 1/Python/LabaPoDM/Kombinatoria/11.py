import typing as tp


def rec(elements: tp.List[tp.Any]) -> tp.Generator[tp.List[tp.Any], None, None]:
    yield []
    for i in range(len(elements)):
        cur = elements[i]
        others = elements[i + 1:]
        for sub in rec(others):
            yield [cur] + sub

n: int = int(input())
for el in rec([i for i in range(1, n + 1)]):
    print(*el)
