def normalize_path(path: str) -> str:
    """
    :param path: unix path to normalize
    :return: normalized path
    """
    if len(path) == 0 or path == '.':
        return '.'

    path_ = path.replace('//', '/')
    arr = [p for p in path_.split('/') if len(p) != 0 and p != '.']
    tmp = []
    absolute = (path_[0] == '/')
    for el in arr:
        if el == '..':
            if len(tmp) != 0:
                if tmp[-1] != '..':
                    tmp.pop()
                else:
                    tmp.append('..')
            else:
                if absolute:
                    pass
                else:
                    tmp.append('..')
        else:
            tmp.append(el)

    if len(tmp) == 0:
        return '/' if absolute else '.'
    result = '/'.join(tmp)
    return '/' + result if absolute else result
