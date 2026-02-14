import pytest

##############
# Code section
##############


# Don't change this function!
def ctr(clicks: int, shows: int) -> float:
    """
    Calculate ctr
    :param clicks: number of clicks on banner
    :param shows: number of banners shows
    :return: clicks-through rate.
             If there are no shows, return 0.0
             If clicks greater then shows, return 1
    """
    return clicks // shows if shows > 0 else 0


def ctr_correct_implementation(clicks: int, shows: int) -> float:
    """
    Calculate ctr. Presumed that clicks always less or equals to shows
    :param clicks: number of clicks on banner
    :param shows: number of banners shows
    :return: clicks-through rate.
             If there are no shows, return 0.0
    """
    if shows == 0 and clicks == 0:
        return float(0)
    elif shows == 0:
        raise AssertionError("Clicks greater than shows")
    elif clicks <= shows:
        return clicks/shows
    else:
        raise AssertionError("Clicks greater than shows")



##############
# Test section
##############

@pytest.mark.skip
def test_check_ctr(clicks: int, shows: int, expected_result: float) -> None:
    """
    Write simple test for defined above function ```ctr```
        which takes function parameters and expected result and assert if something goes wrong with
        "Wrong ctr calculation" message
    :param clicks: parameter for  ctr function
    :param shows: parameter for  ctr function
    :param expected_result: result to compare with
    :return: None
    """
    if abs(ctr(clicks,shows) - expected_result) < 0.01:
        pass
    else:
        raise AssertionError("Wrong ctr calculation")
