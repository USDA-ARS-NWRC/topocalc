import numpy as np
from numba import jit


def adjust_spacing(spacing, skew_angle):
    """Adjust the grid spacing if a skew angle is present

    Arguments:
        spacing {float} -- grid spacing
        skew_angle {float} -- angle to adjust the spacing for [degrees]
    """

    if skew_angle > 45 or skew_angle < 0:
        raise ValueError('skew angle must be between 0 and 45 degrees')

    return spacing / np.cos(skew_angle * np.arctan(1.) / 45)


@jit(nopython=True,parallel=True,fastmath=True)
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
        dx: spacing of the array in the x (sample) direction (if dx=dy, or dx or dy not supplied, spacing is ignored)
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

    slope = np.tan(angle * np.pi / 180.0) * (dy/dx) # unequal dx/dy equivalent to changing skew angle
    max_skew = int((nlines - 1) * slope + 0.5)

    o_nsamps = nsamps
    if fwd:
        o_nsamps += max_skew
    else:
        o_nsamps -= max_skew

    b = np.zeros((nlines, o_nsamps))
    if fill_min:
        b += np.min(arr)

    for line in range(nlines):
        o = line if negflag else nlines - line - 1
        offset = int(o * slope + 0.5)

        if fwd:
            b[line, offset:offset+nsamps] = arr[line, :]
        else:
            b[line, :] = arr[line, offset:offset+o_nsamps]

    return b
