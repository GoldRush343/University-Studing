import typing as tp

def convert_to_common_type(data: list[tp.Any]) -> list[tp.Any]:
    """
    Takes list of multiple types' elements and convert each element to common type according to given rules
    :param data: list of multiple types' elements
    :return: list with elements converted to common type
    """
    # None -> "" None -> ""  None -> 0(float) None -> [] "" -> [] None -> False int -> [] int -> bool
    # list bool float int str None
    types = [str, int, float, bool, tuple, list]
    answer = []
    max_type = 0
    for el in data:
        if not el is None:
            max_type = max(max_type, types.index(type(el)))

    if types[max_type] in [list, tuple]:
        for el in data:
            if el is None or el == "": answer.append([])
            elif type(el) is list: answer.append(el)
            elif type(el) is tuple: answer.append([x for x in el])
            else: answer.append([el])
        return answer

    if types[max_type] is str:
        for el in data:
            if el is None: answer.append("")
            else: answer.append(el)
        return answer

    if types[max_type] is float:
        for el in data:
            if el is None or el == "": answer.append(0.0)
            else: answer.append(float(el))
        return answer

    if types[max_type] is int:
        for el in data:
            if el is None or el == "": answer.append(0)
            else: answer.append(int(el))
        return answer

    if types[max_type] is bool:
        for el in data:
            if el is None or el == "": answer.append(False)
            else: answer.append(bool(el))
        return answer
