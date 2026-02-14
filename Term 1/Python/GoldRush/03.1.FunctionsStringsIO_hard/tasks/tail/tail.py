import os
import sys
import typing as tp
from pathlib import Path

def tail(filename: Path, lines_amount: int = 10, output: tp.IO[bytes] | None = None) -> None:
    """
    :param filename: file to read lines from (the file can be very large)
    :param lines_amount: number of lines to read
    :param output: stream to write requested amount of last lines from file
                   (if nothing specified stdout will be used)
    """
    if lines_amount <= 0:
        return
    if output is None:
        output = sys.stdout.buffer

    chunk_size = 2024
    with open(filename, "rb") as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        pos = file_size

        buffer = bytearray()
        cnt_of_lines = 0

        while pos > 0 and cnt_of_lines <= lines_amount:
            read_size = min(chunk_size, pos)
            pos -= read_size
            f.seek(pos)

            chunk = f.read(read_size)
            buffer = chunk + buffer
            cnt_of_lines = buffer.count(b"\n")

        lines = buffer.split(b'\n')
        if lines and lines[-1] == b'':
            lines = lines[:-1]

        lines_of_lines = lines[-lines_amount:]
        for line in lines_of_lines:
            output.write(line + b'\n')
