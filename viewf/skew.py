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


def skew(arr, angle, fwd=True, fill_min=True):
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

    Args:
        arr: array to skew
        angle: angle between -45 and 45 to skew by
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

    nlines, nsamps = arr.shape

    if angle >= 0.0:
        negflag = False
    else:
        negflag = True
        angle = -angle

    slope = np.tan(angle * np.pi / 180.0)
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
