import heapq
import string
from collections import defaultdict


def normalize(
        text: str
) -> str:
    """
    Removes punctuation and digits and convert to lower case
    :param text: text to normalize
    :return: normalized query
    """
    res: str = ""
    for char in text:
        if not char.isdigit() and char not in string.punctuation:
            res += char
    return res.lower()


def get_words(
        query: str
) -> list[str]:
    """
    Split by words and leave only words with letters greater than 3
    :param query: query to split
    :return: filtered and split query by words
    """
    return [x for x in query.split() if len(x) > 3]


def build_index(
        banners: list[str]
) -> dict[str, list[int]]:
    """
    Create index from words to banners ids with preserving order and without repetitions
    :param banners: list of banners for indexation
    :return: mapping from word to banners ids
    """
    index = defaultdict(list)
    for banner_id, banner in enumerate(banners):
        normalized_banner = normalize(banner)
        words = set(get_words(normalized_banner))
        for word in words:
            index[word].append(banner_id)
    return index


def merge_lists(lists: list[list[int]]) -> list[int]:
    if not lists:
        return []

    pointers = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(pointers)

    result = []
    current = -1
    count = 0

    while pointers:
        value, list_idx, elem_idx = heapq.heappop(pointers)

        if current == -1:
            current = value
            count = 1
        elif value == current:
            count += 1
        else:
            if count == len(lists):
                result.append(current)
            current = value
            count = 1

        if elem_idx + 1 < len(lists[list_idx]):
            next_elem = lists[list_idx][elem_idx + 1]
            heapq.heappush(pointers, (next_elem, list_idx, elem_idx + 1))

    if count == len(lists):
        result.append(current)

    return result


def get_banner_indices_by_query(
        query: str,
        index: dict[str, list[int]]
) -> list[int]:
    """
    Extract banners indices from index, if all words from query contains in indexed banner
    :param query: query to find banners
    :param index: index to search banners
    :return: list of indices of suitable banners
    """
    words = get_words(normalize(query))
    lists = [index[word] for word in words if word in index]
    if len(lists) != len(words):
        return []
    return merge_lists(lists)


#########################
# Don't change this code
#########################

def get_banners(
        query: str,
        index: dict[str, list[int]],
        banners: list[str]
) -> list[str]:
    """
    Extract banners matched to queries
    :param query: query to match
    :param index: word-banner_ids index
    :param banners: list of banners
    :return: list of matched banners
    """
    indices = get_banner_indices_by_query(query, index)
    return [banners[i] for i in indices]

#########################
