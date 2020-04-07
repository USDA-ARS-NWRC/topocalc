import collections

import numpy as np

import hor1d

# import matplotlib.pyplot as plt


def d2r(a): return a * np.pi / 180


def viewf(dem, spacing, nangles=16, slope=None, aspect=None):
    """
    Calculate the sky view factor of a dem

    terrain configuration factor (tvf) is defined as:
        (1 + cos(slope))/2 - sky view factor

    Based on the paper Dozier and Frew, 1990 and modified from
    the Image Processing Workbench code base (Frew, 1990). The
    Python version of sky view factor will be an almost exact
    replication of the IPW command `viewf` minus rounding errors
    from type and linear quantization.

    Args:
        spacing:
        dem:
        nangles:
        slope: sin(slope) with range from 0 to 1
        aspect: Aspect as radians from south (aspect 0 is toward
                the south) with range from -pi to pi, with negative
                values to the west and positive values to the east.

    Returns:
        svf: sky view factor
        tcf: terrain configuration factor

    """

    if dem.ndim != 2:
        raise ValueError('viewf input of dem is not a 2D array')

    if nangles != 16 and nangles != 32:
        raise ValueError('viewf number of angles can be 16 or 32')

    hcos = {}
    Horizon = collections.namedtuple('Horizon', ['azimuth', 'hcos'])

    # East
    # hcos['e'] = Horizon(
    #     d2r(90),
    #     hor1d.hor2d_c(dem, spacing)
    # )

    # # West
    # hcos['w'] = Horizon(
    #     d2r(-90),
    #     hor1d.hor2d_c(dem, spacing, fwd=False)
    # )

    # # SSW
    # t = skew(dem, -22.5).transpose()
    # hcos['ssw'] = Horizon(
    #     d2r(-22.5),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), -22.5, fwd=False)
    # )

    # # NNE
    # hcos['nne'] = Horizon(
    #     d2r(157.5),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), -22.5, fwd=False)
    # )

    # # SW
    t = skew(dem, -45).transpose()
    # hcos['sw'] = Horizon(
    #     d2r(-45),
    #     skew(hor1d.hor2d_c(t, spacing).transpose(), -45, fwd=False)
    # )

    # NE
    hcos['ne'] = Horizon(
        d2r(135),
        skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), -45, fwd=False)
    )

    # # SSE
    # t = skew(dem, 22.5).transpose()
    # hcos['sse'] = Horizon(
    #     d2r(22.5),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), 22.5, fwd=False)
    # )

    # # NNW
    # hcos['nnw'] = Horizon(
    #     d2r(-157.5),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), 22.5, fwd=False)
    # )

    # # SE
    # t = skew(dem, 45).transpose()
    # hcos['se'] = Horizon(
    #     d2r(45),
    #     skew(hor1d.hor2d_c(t, spacing).transpose(), 45, fwd=False)
    # )

    # # NW
    # hcos['nw'] = Horizon(
    #     d2r(-135),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), 45, fwd=False)
    # )

    # # S
    # demt = dem.transpose()
    # hcos['s'] = Horizon(
    #     d2r(0),
    #     hor1d.hor2d_c(demt, spacing).transpose()
    # )

    # # N
    # hcos['n'] = Horizon(
    #     d2r(180),
    #     hor1d.hor2d_c(demt, spacing, fwd=False).transpose()
    # )

    # # ENE
    # t = skew(demt, -22.5).transpose()
    # hcos['ene'] = Horizon(
    #     d2r(112.5),
    #     skew(hor1d.hor2d_c(t, spacing).transpose(), -22.5, fwd=False).transpose()
    # )

    # # WSW
    # hcos['wsw'] = Horizon(
    #     d2r(-67.5),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(), -
    #          22.5, fwd=False).transpose()
    # )

    # # ESE
    # t = skew(demt, 22.5).transpose()
    # hcos['ese'] = Horizon(
    #     d2r(67.5),
    #     skew(hor1d.hor2d_c(t, spacing).transpose(), 22.5, fwd=False).transpose()
    # )

    # # WNW
    # hcos['wnw'] = Horizon(
    #     d2r(-112.5),
    #     skew(hor1d.hor2d_c(t, spacing, fwd=False).transpose(),
    #          22.5, fwd=False).transpose()
    # )

    # sanity check
    for key in hcos.keys():
        assert hcos[key].hcos.shape == dem.shape

    # calculate the gradient if not provided
    # Fill in after PR #125 as it'll be much simpler
    if slope is None:
        pass

    svf, tcf = viewcalc(slope, aspect, hcos)

    return svf, tcf


def viewcalc(slope, aspect, hcos):
    """
    Given the slope, aspect and dictionary of horizon
    angles, calculate the cooresponding sky view and terrain
    configuration factors.

    terrain configuration factor (tvf) is defined as:
    (1 + cos(slope))/2 - sky view factor

    Args:
        slope: sin(slope) with range from 0 to 1
        aspect: Aspect as radians from south (aspect 0 is toward
                the south) with range from -pi to pi, with negative
                values to the west and positive values to the east.
        hcos: cosines of angles to horizon

    Returns:
        svf: sky view factor
        tcf: terrain configuration factor

    """

    if np.max(slope) > 1:
        raise ValueError('viewcalc: slope may not be supplied as sin(S)')

    if np.abs(np.max(aspect)) > np.pi:
        raise ValueError('viewcalc: aspect should range from +/- PI')

    # Trig tables for the constanst values that don't change
    cos_slope, sin_squared, h_mult, cos_aspect = trigtbl(slope, aspect, hcos)

    # perform the integral
    svf = np.zeros_like(slope)
    for key in hcos.keys():
        intgrnd = cos_slope * sin_squared[key] + \
            slope * cos_aspect[key] * h_mult[key]
        svf[intgrnd > 0] += intgrnd[intgrnd > 0]

        svf = h_mult[key]

    svf = svf / len(hcos)

    tcf = (1 + cos_slope)/2 - svf

    return svf, tcf


def trigtbl(slope, aspect, hcos):
    """
    Calculate the trigometic relationship of the sky view factor using
    equation 7b from Dozier and Frew 1990

    .. math::
        V_d \approx \frac{1}{2\pi} \int_{0}^{2\pi}\left [ cos(S) sin^2{H_\phi} + sin(S)cos(\phi-A)
        \times \left ( H_\phi - sin(H_\phi) cos(H_\phi) \right )\right ] d\phi

    Args:
        slope: sin(slope) with range from 0 to 1
        aspect: Aspect as radians from south (aspect 0 is toward
                the south) with range from -pi to pi, with negative
                values to the west and positive values to the east.
        hcos: cosines of angles to horizon
    """

    # cosine of slopes, slope is provided as sin(slope)
    cos_slope = np.sqrt((1 - slope) * (1 + slope))

    # sines and values of horizon angles from zenith
    sin_squared = {key: None for key in hcos.keys()}
    h_mult = {key: None for key in hcos.keys()}
    cos_aspect = {key: None for key in hcos.keys()}
    for key, h in hcos.items():
        # sin squared of horizon
        sin_squared[key] = (1 - h.hcos) * (1 + h.hcos)

        # H - sin(H)cos(H)
        h_mult[key] = np.arccos(h.hcos) - np.sqrt(sin_squared[key]) * h.hcos

        # cosines of difference between horizon aspect and slope aspect
        cos_aspect[key] = np.cos(h.azimuth - aspect)

    return cos_slope, sin_squared, h_mult, cos_aspect


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
        fill_min: While IPW skew says it fills with zeros, the output image isn't

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
