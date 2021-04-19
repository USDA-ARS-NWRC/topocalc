import numpy as np


def adjust_spacing(spacing, skew_angle):
    """Adjust the grid spacing if a skew angle is present

    Arguments:
        spacing {float} -- grid spacing
        skew_angle {float} -- angle to adjust the spacing for [degrees]
    """

    if skew_angle > 45 or skew_angle < 0:
        raise ValueError('skew angle must be between 0 and 45 degrees')

    return spacing / np.cos(skew_angle * np.arctan(1.) / 45)


def custom_roll(arr, r_tup):
    """Apply an independent roll for each row of an array.

    Taken from https://stackoverflow.com/a/60460462

    Parameters
    ----------
    arr: np.ndarray
        2d array
    r_tup: np.ndarray
        1d array of shifts for each row of the 2d array
    """

    m = np.asarray(r_tup)
    arr_roll = arr[:, [*range(arr.shape[1]),
                       *range(arr.shape[1]-1)]].copy()  # need `copy`
    strd_0, strd_1 = arr_roll.strides
    n = arr.shape[1]
    result = np.lib.stride_tricks.as_strided(arr_roll,
                                             (*arr.shape, n),
                                             (strd_0, strd_1, strd_1))

    return result[np.arange(arr.shape[0]), (n - m) % n]


def skew(arr, angle, dx=None, dy=None, fwd=True, fill_min=True):
    """
    Skew the origin of successive lines by a specified angle
    A skew with angle of 30 degrees causes the following transformation:

        +-----------+       +---------------+
        |           |       |000/          /|
        |   input   |       |00/  output  /0|
        |   image   |       |0/   image  /00|
        |           |       |/          /000|
        +-----------+       +---------------+

    Calling skew with fwd=False will return the output image
    back to the input image.

    Skew angle must be between -45 and 45 degrees

    Arguments:
        arr: array to skew
        angle: angle between -45 and 45 to skew by
        dx: spacing of the array in the x (sample) direction
            (if dx=dy, or dx or dy not supplied, spacing is ignored)
        dy: spacing of the array in the y (line) direction
        fwd: add skew to image if True, unskew image if False
        fill_min: While IPW skew says it fills with zeros, the output
            image is filled with the minimum value

    Returns:
        skewed array

    """

    if angle == 0:
        return arr

    if angle > 45 or angle < -45:
        raise ValueError('skew angle must be between -45 and 45 degrees')

    if dx is None or dy is None:
        dx = 1.0
        dy = 1.0

    nlines, nsamps = arr.shape

    if angle >= 0.0:
        negflag = False
    else:
        negflag = True
        angle = -angle

    # unequal dx/dy equivalent to changing skew angle
    slope = np.tan(angle * np.pi / 180.0) * (dy/dx)
    max_skew = int((nlines - 1) * slope + 0.5)

    o_nsamps = nsamps
    if fwd:
        o_nsamps += max_skew
    else:
        o_nsamps -= max_skew

    b = np.zeros((nlines, o_nsamps))
    if fill_min:
        b += np.min(arr)

    # if skewing, first fill output array with original array
    if fwd:
        b[0:nlines, 0:nsamps] = arr

    o = np.arange(nlines)
    # positive skew angle means shifts decrease with increasing row index
    if not negflag:
        o = nlines - o - 1

    offset = (o * slope + 0.5).astype(int)

    if not fwd:  # offset values are negative shifts if unskewing
        offset *= -1

    if fwd:
        b = custom_roll(b, offset)
    else:
        # assignment indexing added to ensure array shape match
        b[:, :] = custom_roll(arr, offset)[:, :o_nsamps]

    """
    for line in range(nlines):
        o = line if negflag else nlines - line - 1
        offset = int(o * slope + 0.5)

        if fwd:
            b[line, offset:offset+nsamps] = arr[line, :]
        else:
            b[line, :] = arr[line, offset:offset+o_nsamps]
    """
    return b
