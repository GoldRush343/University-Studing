def get_common_type(type1: type, type2: type) -> type:
    """
    Calculate common type according to rule, that it must have the most adequate interpretation after conversion.
    Look in tests for adequacy calibration.
    :param type1: one of [bool, int, float, complex, list, range, tuple, str] types
    :param type2: one of [bool, int, float, complex, list, range, tuple, str] types
    :return: the most concrete common type, which can be used to convert both input values
    """
    to_list = [range, tuple, list, str]
    to_num = [bool, int, float, complex]
    if type1 == range and type2 == range:
        return tuple
    if type1 in to_list and type2 in to_list:
        t1 = to_list.index(type1)
        t2 = to_list.index(type2)
        return to_list[max(t1, t2)]
    if type1 in to_num and type2 in to_num:
        t1 = to_num.index(type1)
        t2 = to_num.index(type2)
        return to_num[max(t1, t2)]
    else:
        return str
