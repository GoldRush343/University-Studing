import heapq
import typing as tp


def merge(seq: tp.Sequence[tp.Sequence[int]]) -> list[int]:
    """
    :param seq: sequence of sorted sequences
    :return: merged sorted list
    """
    heap = []
    index = [0]*len(seq)
    result = []
    for i, cur_seq in enumerate(seq):
        if cur_seq:
            heapq.heappush(heap, (cur_seq[0], i))

    while heap:
        num, id_seq = heapq.heappop(heap)
        result.append(num)
        index[id_seq] += 1
        if index[id_seq] < len(seq[id_seq]):
            next_num = seq[id_seq][index[id_seq]]
            heapq.heappush(heap, (next_num, id_seq))
    return result

