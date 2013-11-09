"""Simple averaging smoother."""

import numpy as np


def smooth(x, y, degree=3):
    """Smooth y-values and return new x, y pair."""

    if degree == 1:
        return x, y
    elif not isodd(degree):
        raise ValueError("Degree must be an odd number")
    else:
        window_width = int(degree / 2)
        data_size = len(y) - degree + 1

        smoothed_y = np.zeros(data_size)
        for idx in range(degree):
            smoothed_y += y[idx:idx + data_size]
        smoothed_y /= degree

        smoothed_x = x[window_width:-window_width]

        return smoothed_x, smoothed_y


def isodd(x):
    """Determine if number is odd.

    :return: boolean

    """
    if x % 2 == 1:
        return True
    else:
        return False
