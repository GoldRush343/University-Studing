import enum


class Status(enum.Enum):
    NEW = 0
    EXTRACTED = 1
    FINISHED = 2


def extract_alphabet(
        graph: dict[str, set[str]]
) -> list[str]:
    """
    Extract alphabet from graph
    :param graph: graph with partial order
    :return: alphabet
    """
    status: dict[str, Status] = {char: Status.NEW for char in graph}
    result: list[str] = []
    stack: list[str] = []

    for char in graph:
        if status[char] != Status.NEW:
            continue
        stack.append(char)
        while stack:
            cur = stack[-1]
            if status[cur] == Status.NEW:
                status[cur] = Status.EXTRACTED
                for neighbor in graph[cur]:
                    if status[neighbor] == Status.NEW:
                        stack.append(neighbor)
            elif status[cur] == Status.EXTRACTED:
                status[cur] = Status.FINISHED
                result.append(cur)
                stack.pop()
            else:
                stack.pop()
    return result[::-1]


def build_graph(
        words: list[str]
) -> dict[str, set[str]]:
    """
    Build graph from ordered words. Graph should contain all letters from words
    :param words: ordered words
    :return: graph
    """
    res: dict[str, set[str]] = {}
    for word in words:
        for char in word:
            if char not in res:
                res[char] = set()
    for word1, word2 in zip(words, words[1:]):
        i: int = 0
        while i < min(len(word1), len(word2)) and word1[i] == word2[i]:
            i += 1
        if i >= min(len(word1), len(word2)):
            continue
        res[word1[i]].add(word2[i])
    return res


#########################
# Don't change this code
#########################

def get_alphabet(
        words: list[str]
) -> list[str]:
    """
    Extract alphabet from sorted words
    :param words: sorted words
    :return: alphabet
    """
    graph = build_graph(words)
    return extract_alphabet(graph)

#########################
