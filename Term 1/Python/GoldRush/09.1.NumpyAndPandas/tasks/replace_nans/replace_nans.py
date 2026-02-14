import numpy as np
import numpy.typing as npt


def replace_nans(matrix: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    Replace all nans in matrix with average of other values.
    If all values are nans, then return zero matrix of the same size.
    :param matrix: matrix,
    :return: replaced matrix
    """
    mask = np.isnan(matrix)
    if np.all(mask):
        return np.zeros_like(matrix)

    mean_val = np.nanmean(matrix)
    return np.where(mask, mean_val, matrix)
