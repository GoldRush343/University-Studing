import zlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BlobType(Enum):
    """Helper class for holding blob type"""
    COMMIT = b'commit'
    TREE = b'tree'
    DATA = b'blob'

    @classmethod
    def from_bytes(cls, type_: bytes) -> 'BlobType':
        for member in cls:
            if member.value == type_:
                return member
        assert False, f'Unknown type {type_.decode("utf-8")}'


@dataclass
class Blob:
    """Any blob holder"""
    type_: BlobType
    content: bytes


@dataclass
class Commit:
    """Commit blob holder"""
    tree_hash: str
    parents: list[str]
    author: str
    committer: str
    message: str


@dataclass
class Tree:
    """Tree blob holder"""
    children: dict[str, Blob]


def read_blob(path: Path) -> Blob:
    """
    Read blob-file, decompress and parse header
    :param path: path to blob-file
    :return: blob-file type and content
    """
    data = path.read_bytes()
    decompressed = zlib.decompress(data)
    header, _, content_ = decompressed.partition(b'\x00')
    type_, _, lenght = header.partition(b' ')
    blob = Blob(
        type_ = BlobType.from_bytes(type_),
        content = content_
    )
    return blob


def traverse_objects(obj_dir: Path) -> dict[str, Blob]:
    """
    Traverse directory with git objects and load them
    :param obj_dir: path to git "objects" directory
    :return: mapping from hash to blob with every blob found
    """
    res = dict()
    for dir in obj_dir.iterdir():
        if dir.is_dir():
            for file in dir.iterdir():
                blob = read_blob(file)
                hash = f'{dir.name}{file.name}'
                res[hash] = blob
    return res


def parse_commit(blob: Blob) -> Commit:
    """
    Parse commit blob
    :param blob: blob with commit type
    :return: parsed commit
    """
    tree_hash: str = ""
    parents: list[str] = list()
    author: str = ""
    committer: str = ""
    header, message = blob.content.split(b'\n\n', 1)

    for line in header.split(b'\n'):
        key, _, value = line.partition(b' ')
        if key == b'tree':
            tree_hash = value.decode('utf-8')
        elif key == b'parent':
            parents.append(value.decode('utf-8'))
        elif key == b'author':
            author = value.decode('utf-8')
        elif key == b'committer':
            committer = value.decode('utf-8')

    if message.endswith(b'\n'):
        message = message[:-1]

    commit = Commit(
        tree_hash = tree_hash,
        parents = parents,
        author= author,
        committer=committer,
        message = message.decode('utf-8')
    )
    return commit


def parse_tree(blobs: dict[str, Blob], tree_root: Blob, ignore_missing: bool = True) -> Tree:
    """
    Parse tree blob
    :param blobs: all read blobs (by traverse_objects)
    :param tree_root: tree blob to parse
    :param ignore_missing: ignore blobs which were not found in objects directory
    :return: tree contains children blobs (or only part of them found in objects directory)
    NB. Children blobs are not being parsed according to type.
        Also nested tree blobs are not being traversed.
    """
    data = tree_root.content
    children = {}
    pos = 0

    while pos < len(data):
        delim = data.find(b'\x00', pos)
        if delim == -1:
            break

        header = data[pos:delim]
        mode, _, name = header.partition(b' ')

        bytes = data[delim + 1: delim + 21]
        hash = bytes.hex()

        if hash in blobs:
            children[name.decode('utf-8')] = blobs[hash]

        pos = delim + 21

    return Tree(
        children=children
    )


def find_initial_commit(blobs: dict[str, Blob]) -> Commit:
    """
    Iterate over blobs and find initial commit (without parents)
    :param blobs: blobs read from objects dir
    :return: initial commit
    """
    for _, blob in blobs.items():
        if blob.type_ == BlobType.COMMIT:
            commit = parse_commit(blob)
            if not commit.parents:
                return commit
    raise ValueError("Initial commit not found")


def search_file(blobs: dict[str, Blob], tree_root: Blob, filename: str) -> Blob:
    """
    Traverse tree blob (can have nested tree blobs) and find requested file,
    check if file was not found (assertion).
    :param blobs: blobs read from objects dir
    :param tree_root: root blob for traversal
    :param filename: requested file
    :return: requested file blob
    """
    tree: Tree = parse_tree(blobs, tree_root)
    children = tree.children

    for name, blob in children.items():
        if blob.type_ == BlobType.DATA:
            if name == filename:
                return blob
        elif blob.type_ == BlobType.TREE:
            return search_file(blobs, blob, filename)

    raise FileNotFoundError(f'File {filename} not found')
