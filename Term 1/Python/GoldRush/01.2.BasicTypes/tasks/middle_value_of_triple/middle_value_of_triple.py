def get_middle_value(a: int, b: int, c: int) -> int:
    """
    Takes three values and returns middle value.
    """
    # if a <= b <= c or c <= b <= a:
    #     return b
    # elif b <= c <= a or a <= c <= b:
    #     return c
    # else:
    #     return a
    return sum([a,b,c]) - max(a,b,c) - min(a,b,c)

