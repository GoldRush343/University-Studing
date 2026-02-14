from collections.abc import Sequence

def find_median(nums1: Sequence[int], nums2: Sequence[int]) -> float:
    """
    Find median of two sorted sequences. At least one of sequences should be not empty.
    :param nums1: sorted sequence of integers
    :param nums2: sorted sequence of integers
    :return: middle value if sum of sequences' lengths is odd
             average of two middle values if sum of sequences' lengths is even
    """
    # num1: lt n num2: rt m
    inf = 1e9
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    n, m = len(nums1), len(nums2)
    lt = n // 2
    rt = (m + n + 1) // 2 - lt  # formula for nums2 division
    while True:
        L1 = -inf if lt == 0 else nums1[lt - 1]
        L2 = -inf if rt == 0 else nums2[rt - 1]

        R1 = inf if lt == n else nums1[lt]
        R2 = inf if rt == m else nums2[rt]

        if L1 <= R2 and L2 <= R1:  # found answer
            if (n + m) % 2 == 0:
                return (max(L1, L2) + min(R1, R2)) / 2
            else:
                return float(max(L1, L2))
        if L1 > R2:  # <-division
            lt -= 1
            rt += 1
        else:  # division->
            lt += 1
            rt -= 1
