import typing as tp


def revert(dct: tp.Mapping[str, str]) -> dict[str, list[str]]:
    """
    :param dct: dictionary to revert in format {key: value}
    :return: reverted dictionary {value: [key1, key2, key3]}
    """
    ans = dict()
    for key, val in dct.items():
        if val in ans.keys():
            ans[val] += [key]
        else:
            ans[val] = [key]
    return ans

