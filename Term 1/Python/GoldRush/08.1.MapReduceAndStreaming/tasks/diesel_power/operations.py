import heapq
import re
import string
import typing as tp
from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import groupby

TRow = dict[str, tp.Any]
TRowsIterable = tp.Iterable[TRow]
TRowsGenerator = tp.Generator[TRow, None, None]


class Operation(ABC):
    @abstractmethod
    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        pass


class Read(Operation):
    def __init__(self, filename: str, parser: tp.Callable[[str], TRow]) -> None:
        self._filename = filename
        self._parser = parser

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        with open(self._filename) as f:
            for line in f:
                yield self._parser(line)


class ReadIterFactory(Operation):
    def __init__(self, name: str) -> None:
        self._name = name

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in kwargs[self._name]():
            yield row


# Operations


class Mapper(ABC):
    """Base class for mappers"""
    @abstractmethod
    def __call__(self, row: TRow) -> TRowsGenerator:
        """
        :param row: one table row
        """
        pass


class Map(Operation):
    def __init__(self, mapper: Mapper) -> None:
        self._mapper = mapper

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for row in rows:
            yield from self._mapper(row)


class Reducer(ABC):
    """Base class for reducers"""
    @abstractmethod
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        """
        :param rows: table rows
        """
        pass


class Reduce(Operation):
    def __init__(self, reducer: Reducer, keys: tp.Sequence[str]) -> None:
        self._reducer = reducer
        self._keys = keys

    def key_func(self, r):
        return tuple(str(r[k]) for k in self._keys)

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        for key, group in groupby(rows, key=self.key_func):
            yield from self._reducer(key, group)


class Joiner(ABC):
    """Base class for joiners"""
    def __init__(self, suffix_a: str = '_1', suffix_b: str = '_2') -> None:
        self._a_suffix = suffix_a
        self._b_suffix = suffix_b

    def _merge_rows(self, keys: tp.Sequence[str], row_a: TRow, row_b: TRow) -> TRow:
        new_row = row_a.copy()
        keys_set = set(keys)

        common_cols = (row_a.keys() & row_b.keys()) - keys_set

        for col in common_cols:
            val = new_row.pop(col)
            new_row[f"{col}{self._a_suffix}"] = val

        for col, val in row_b.items():
            if col in keys_set:
                continue

            if col in common_cols:
                new_row[f"{col}{self._b_suffix}"] = val
            else:
                new_row[col] = val

        return new_row

    @abstractmethod
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        """
        :param keys: join keys
        :param rows_a: left table rows
        :param rows_b: right table rows
        """
        pass


class Join(Operation):
    def __init__(self, joiner: Joiner, keys: tp.Sequence[str]):
        self._keys = keys
        self._joiner = joiner

    def key_func(self, r):
        return tuple(str(r[k]) for k in self._keys)

    def __call__(self, rows: TRowsIterable, *args: tp.Any, **kwargs: tp.Any) -> TRowsGenerator:
        rows_a = rows
        rows_b = args[0]

        it_a = groupby(rows_a, key=self.key_func)
        it_b = groupby(rows_b, key=self.key_func)

        def get_next_group(iterator):
            try:
                return next(iterator)
            except StopIteration:
                return None, None

        key_a, group_a = get_next_group(it_a)
        key_b, group_b = get_next_group(it_b)

        while key_a is not None or key_b is not None:
            if key_a is not None and key_b is not None and key_a == key_b:
                yield from self._joiner(self._keys, group_a, group_b)
                key_a, group_a = get_next_group(it_a)
                key_b, group_b = get_next_group(it_b)

            elif key_b is None or (key_a is not None and key_a < key_b):
                yield from self._joiner(self._keys, group_a, [])
                key_a, group_a = get_next_group(it_a)

            else:
                yield from self._joiner(self._keys, [], group_b)
                key_b, group_b = get_next_group(it_b)


# Dummy operators


class DummyMapper(Mapper):
    """Yield exactly the row passed"""
    def __call__(self, row: TRow) -> TRowsGenerator:
        yield row


class FirstReducer(Reducer):
    """Yield only first row from passed ones"""
    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        for row in rows:
            yield row
            break


# Mappers


class FilterPunctuation(Mapper):
    """Left only non-punctuation symbols"""
    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self._column = column
        self._translator = str.maketrans('', '', string.punctuation)

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        if self._column in new_row:
            text = str(new_row[self._column])
            new_row[self._column] = text.translate(self._translator)
        yield new_row


class LowerCase(Mapper):
    """Replace column value with value in lower case"""
    def __init__(self, column: str):
        """
        :param column: name of column to process
        """
        self._column = column

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        if self._column in new_row:
            new_row[self._column] = str(new_row[self._column]).lower()
        yield new_row


class Split(Mapper):
    """Split row on multiple rows by separator"""
    def __init__(self, column: str, separator: str | None = None) -> None:
        """
        :param column: name of column to split
        :param separator: string to separate by
        """
        self._column = column
        self._separator = separator

    def __call__(self, row: TRow) -> TRowsGenerator:
        text = str(row.get(self._column, ''))

        if self._separator is None:
            for match in re.finditer(r'\S+', text):
                new_row = row.copy()
                new_row[self._column] = match.group()
                yield new_row
        else:
            start = 0
            sep_len = len(self._separator)

            while True:
                idx = text.find(self._separator, start)
                if idx == -1:
                    chunk = text[start:]
                    new_row = row.copy()
                    new_row[self._column] = chunk
                    yield new_row
                    break

                chunk = text[start:idx]
                new_row = row.copy()
                new_row[self._column] = chunk
                yield new_row

                start = idx + sep_len


class Product(Mapper):
    """Calculates product of multiple columns"""
    def __init__(self, columns: tp.Sequence[str], result_column: str = 'product') -> None:
        """
        :param columns: column names to product
        :param result_column: column name to save product in
        """
        self._columns = columns
        self._result_column = result_column

    def __call__(self, row: TRow) -> TRowsGenerator:
        new_row = row.copy()
        result = 1.0
        for col in self._columns:
            val = row.get(col, 0)
            try:
                result *= float(val)
            except (ValueError, TypeError):
                result = 0.0
                break

        new_row[self._result_column] = result if not result.is_integer() else int(result)
        yield new_row


class Filter(Mapper):
    """Remove records that don't satisfy some condition"""
    def __init__(self, condition: tp.Callable[[TRow], bool]) -> None:
        """
        :param condition: if condition is not true - remove record
        """
        self._condition = condition

    def __call__(self, row: TRow) -> TRowsGenerator:
        if self._condition(row):
            yield row


class Project(Mapper):
    """Leave only mentioned columns"""
    def __init__(self, columns: tp.Sequence[str]) -> None:
        """
        :param columns: names of columns
        """
        self._columns = columns

    def __call__(self, row: TRow) -> TRowsGenerator:
        yield {k: row[k] for k in self._columns if k in row}


# Reducers


class TopN(Reducer):
    """Calculate top N by value"""
    def __init__(self, column: str, n: int) -> None:
        """
        :param column: column name to get top by
        :param n: number of top values to extract
        """
        self._column_max = column
        self._n = n

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        heap = []
        for i, row in enumerate(rows):
            val = row.get(self._column_max)
            if val is None:
                continue

            item = (val, i, row)

            if len(heap) < self._n:
                heapq.heappush(heap, item)
            else:
                if val > heap[0][0]:
                    heapq.heapreplace(heap, item)

        result = sorted(heap, key=lambda x: x[0], reverse=True)
        for _, _, row in result:
            yield row


class TermFrequency(Reducer):
    """Calculate frequency of values in column"""

    def __init__(self, words_column: str, result_column: str = 'tf') -> None:
        """
        :param words_column: name for column with words
        :param result_column: name for result column
        """
        self._words_column = words_column
        self._result_column = result_column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        total_count = 0
        word_counts = defaultdict(int)
        row_templates = {}

        for row in rows:
            total_count += 1
            word = row.get(self._words_column)
            word_counts[word] += 1

            if word not in row_templates:
                row_templates[word] = row

        if total_count == 0:
            return

        for word, count in word_counts.items():
            template = row_templates[word]
            new_row = template.copy()

            if 'count' in new_row:
                del new_row['count']

            new_row[self._result_column] = count / total_count
            yield new_row


class Count(Reducer):
    """
    Count records by key
    Example for group_key=('a',) and column='d'
        {'a': 1, 'b': 5, 'c': 2}
        {'a': 1, 'b': 6, 'c': 1}
        =>
        {'a': 1, 'd': 2}
    """

    def __init__(self, column: str) -> None:
        """
        :param column: name for result column
        """
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        count: int = 0
        template = None
        for row in rows:
            if template is None:
                template = row
            count += 1 #type: ignore

        if template is not None:
            new_row = template.copy()
            new_row[self._column] = count
            if 'sentence_id' in new_row:
                del new_row['sentence_id']
            yield new_row


class Sum(Reducer):
    """
    Sum values aggregated by key
    Example for key=('a',) and column='b'
        {'a': 1, 'b': 2, 'c': 4}
        {'a': 1, 'b': 3, 'c': 5}
        =>
        {'a': 1, 'b': 5}
    """

    def __init__(self, column: str) -> None:
        """
        :param column: name for sum column
        """
        self._column = column

    def __call__(self, group_key: tuple[str, ...], rows: TRowsIterable) -> TRowsGenerator:
        total = 0.0
        template = None
        for row in rows:
            if template is None:
                template = row
            val = row.get(self._column, 0)
            try:
                total += float(val) #type: ignore
            except (TypeError, ValueError):
                pass

        if template is not None:
            new_row = template.copy()
            new_row[self._column] = total if not total.is_integer() else int(total)
            if 'player_id' in new_row:
                del new_row['player_id']
            yield new_row


# Joiners


class InnerJoiner(Joiner):
    """Join with inner strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        cached_b = list(rows_b)
        if not cached_b:
            return

        for row_a in rows_a:
            for row_b in cached_b:
                yield self._merge_rows(keys, row_a, row_b)


class OuterJoiner(Joiner):
    """Join with outer strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        cached_b = list(rows_b)

        has_a = False
        for row_a in rows_a:
            has_a = True
            if cached_b:
                for row_b in cached_b:
                    yield self._merge_rows(keys, row_a, row_b)
            else:
                yield self._merge_rows(keys, row_a, {})

        if not has_a and cached_b:
            for row_b in cached_b:
                fake_a = {k: row_b[k] for k in keys if k in row_b}
                yield self._merge_rows(keys, fake_a, row_b)


class LeftJoiner(Joiner):
    """Join with left strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        cached_b = list(rows_b)

        for row_a in rows_a:
            if cached_b:
                for row_b in cached_b:
                    yield self._merge_rows(keys, row_a, row_b)
            else:
                yield self._merge_rows(keys, row_a, {})


class RightJoiner(Joiner):
    """Join with right strategy"""
    def __call__(self, keys: tp.Sequence[str], rows_a: TRowsIterable, rows_b: TRowsIterable) -> TRowsGenerator:
        cached_a = list(rows_a)

        if not cached_a:
            for row_b in rows_b:
                fake_a = {k: row_b[k] for k in keys if k in row_b}
                yield self._merge_rows(keys, fake_a, row_b)
            return

        for row_b in rows_b:
            for row_a in cached_a:
                yield self._merge_rows(keys, row_a, row_b)
