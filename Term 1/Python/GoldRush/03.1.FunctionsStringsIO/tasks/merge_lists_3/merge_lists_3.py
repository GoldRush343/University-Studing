import heapq
import typing as tp


def merge(input_streams: tp.Sequence[tp.IO[bytes]], output_stream: tp.IO[bytes]) -> None:
    """
    Merge input_streams in output_stream
    :param input_streams: list of input streams. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :param output_stream: output stream. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :return: None
    """
    heap = []
    for i, stream in enumerate(input_streams):
        line = stream.readline()
        if line:
            heapq.heappush(heap, (int(line), i, line))

    while heap:
        num, id, line = heapq.heappop(heap)
        output_stream.write(line)
        next_line = input_streams[id].readline()
        if next_line:
            heapq.heappush(heap, (int(next_line), id, next_line))
