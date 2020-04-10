import collections

import numpy as np

from viewf.horizon import horizon

# import matplotlib.pyplot as plt


def d2r(a): return a * np.pi / 180


def viewf(dem, spacing, nangles=16, sin_slope=None, aspect=None):
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
        sin_slope: sin(slope) with range from 0 to 1
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

    if np.max(sin_slope) > 1:
        raise ValueError('slope must be sin(slope) with range from 0 to 1')

    Horizon = collections.namedtuple('Horizon', ['azimuth', 'hcos'])

    # -180 is North
    angles = np.linspace(-180, 180, num=nangles, endpoint=False)

    hcos = {}
    angles = [90]
    for angle in angles:
        h = horizon(angle, dem, spacing)
        hcos[angle] = Horizon(d2r(angle), h)

    # calculate the gradient if not provided
    # Fill in after PR #125 as it'll be much simpler
    if sin_slope is None:
        pass

    svf, tcf = viewcalc(sin_slope, aspect, hcos)

    return svf, tcf


def viewcalc(sin_slope, aspect, hcos):
    """
    Given the slope, aspect and dictionary of horizon
    angles, calculate the cooresponding sky view and terrain
    configuration factors.

    terrain configuration factor (tvf) is defined as:
    (1 + cos(slope))/2 - sky view factor

    Args:
        sin_slope: sin(slope) with range from 0 to 1
        aspect: Aspect as radians from south (aspect 0 is toward
                the south) with range from -pi to pi, with negative
                values to the west and positive values to the east.
        hcos: cosines of angles to horizon

    Returns:
        svf: sky view factor
        tcf: terrain configuration factor

    """

    if np.max(sin_slope) > 1:
        raise ValueError('viewcalc: slope may not be supplied as sin(S)')

    if np.abs(np.max(aspect)) > np.pi:
        raise ValueError('viewcalc: aspect should range from +/- PI')

    # Trig tables for the constanst values that don't change
    cos_slope, sin_squared, h_mult, cos_aspect = trigtbl(
        sin_slope, aspect, hcos)

    # perform the integral
    svf = np.zeros_like(sin_slope)
    for key in hcos.keys():

        intgrnd = cos_slope * sin_squared[key] + \
            sin_slope * cos_aspect[key] * h_mult[key]

        svf = svf + intgrnd

        # ind = intgrnd > 0
        # svf[ind] = svf[ind] + intgrnd[ind]

    svf = svf / len(hcos)

    tcf = (1 + cos_slope)/2 - svf

    return svf, tcf


def trigtbl(sin_slope, aspect, hcos):
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

    # cosine of slopes, sin_slope is provided as sin(slope)
    cos_slope = np.sqrt((1 - sin_slope) * (1 + sin_slope))

    # sines and values of horizon angles from zenith
    sin_squared = {key: None for key in hcos.keys()}
    h_mult = {key: None for key in hcos.keys()}
    cos_aspect = {key: None for key in hcos.keys()}
    for key, h in hcos.items():
        # sin squared of horizon sin2H
        sin_squared[key] = (1 - h.hcos) * (1 + h.hcos)

        # H - sin(H)cos(H)
        h_mult[key] = np.arccos(h.hcos) - np.sqrt(sin_squared[key]) * h.hcos

        # cosines of difference between horizon aspect and slope aspect
        # cos(phi - aspect)
        cos_aspect[key] = np.cos(h.azimuth - aspect)

    return cos_slope, sin_squared, h_mult, cos_aspect
