from sqlalchemy import false


def find_value(nums: list[int] | range, value: int) -> bool:
    """
    Find value in sorted sequence
    :param nums: sequence of integers. Could be empty
    :param value: integer to find
    :return: True if value exists, False otherwise
    """
    # l correct t not correct
    l, r = -1, len(nums)
    while r - l > 1:
        m = (r + l)//2
        if nums[m] < value:
            l = m
        else:
            r = m
    if r == len(nums):
        return False
    elif nums[r] != value:
        return False
    else:
        return True
