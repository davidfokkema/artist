"""Recursive linear interpolation smoother."""

import numpy as np


def smooth(x, y, degree=1, logx=False, logy=False):
    """Smooth y-values and return new x, y pair.

    :param x,y: data values
    :param degree: degree of smoothing

    Smooth data by using a recursive linear interpolation technique.  For
    degree = 0, return the original values.  For degree = 1, generate a
    evenly spaced sequence of x-values, with the length equal to the
    original length.  The y-values are linearly interpolated for these
    x-values.  For degree >= 2, calls itself with degree - 1, then
    calculates new x-values by taking the averages of the returned
    x-values, and calculates new y-values by linear interpolation.  The
    return values are thus reduced in length by one sample.

    """
    if degree == 0:
        return x, y
    else:
        if logx:
            x = np.log10(x)
        if logy:
            y = np.log10(y)

        if degree == 1:
            # generate new linearly spaced x-points
            smoothed_x = np.linspace(min(x), max(x), len(x))
            # generate new y-points using linear interpolation
            smoothed_y = np.interp(smoothed_x, x, y)
        else:
            # smooth data by linear interpolation
            x, y = smooth(x, y, degree - 1)
            smoothed_x = (x[:-1] + x[1:]) / 2
            smoothed_y = np.interp(smoothed_x, x, y)

        if logx:
            smoothed_x = 10 ** smoothed_x
        if logy:
            smoothed_y = 10 ** smoothed_y

        return smoothed_x, smoothed_y
