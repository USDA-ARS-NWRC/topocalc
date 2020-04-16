import collections

import numpy as np

from topocalc.gradient import gradient_d8
from topocalc.horizon import horizon


def d2r(a):
    """Angle to radians

    Arguments:
        a {float} -- angle in degrees

    Returns:
        v {float} -- angle in radians
    """
    v = a * np.pi / 180
    v = round(v, 6)  # just for testing at the moment
    return v


def viewf(dem, spacing, nangles=72, sin_slope=None, aspect=None):
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
        dem: numpy array for the DEM
        spacing: grid spacing of the DEM
        nangles: number of angles to estimate the horizon, defaults
                to 72 angles
        sin_slope: optional, will calculate if not provided
                    sin(slope) with range from 0 to 1
        aspect: optional, will calculate if not provided
                Aspect as radians from south (aspect 0 is toward
                the south) with range from -pi to pi, with negative
                values to the west and positive values to the east.

    Returns:
        svf: sky view factor
        tcf: terrain configuration factor

    """

    if dem.ndim != 2:
        raise ValueError('viewf input of dem is not a 2D array')

    if nangles < 16:
        raise ValueError('viewf number of angles should be 16 or greater')

    if sin_slope is not None:
        if np.max(sin_slope) > 1:
            raise ValueError('slope must be sin(slope) with range from 0 to 1')

    Horizon = collections.namedtuple('Horizon', ['azimuth', 'hcos'])

    # -180 is North
    angles = np.linspace(-180, 180, num=nangles, endpoint=False)

    hcos = {}
    for angle in angles:
        h = horizon(angle, dem, spacing)
        hcos[angle] = Horizon(d2r(angle), h)

    # calculate the gradient if not provided
    # The slope is returned as radians so convert to sin(S)
    if sin_slope is None:
        slope, aspect = gradient_d8(
            dem, dx=spacing, dy=spacing, aspect_rad=True)
        sin_slope = np.sin(slope)

    svf, tcf = viewcalc(sin_slope, aspect, hcos)

    return svf, tcf


def viewcalc(sin_slope, aspect, hcos):
    """
    Given the slope, aspect and dictionary of horizon
    angles, calculate the cooresponding sky view and terrain
    configuration factors.

    Calculate the sky view factor using equation 7b from Dozier and Frew 1990

    .. math::
        V_d \approx \frac{1}{2\pi} \int_{0}^{2\pi}\left [ cos(S) sin^2{H_\phi} 
        + sin(S)cos(\phi-A) \times \left ( H_\phi - sin(H_\phi) cos(H_\phi)
        \right )\right ] d\phi

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

    """  # noqa

    if np.max(sin_slope) > 1:
        raise ValueError('viewcalc: slope may not be supplied as sin(S)')

    if np.abs(np.max(aspect)) > np.pi:
        raise ValueError('viewcalc: aspect should range from +/- PI')

    # perform the integral
    cos_slope = np.sqrt((1 - sin_slope) * (1 + sin_slope))
    svf = np.zeros_like(sin_slope)
    for key, h in hcos.items():

        # sin^2(H)
        sin_squared = (1 - h.hcos) * (1 + h.hcos)

        # H - sin(H)cos(H)
        h_mult = np.arccos(h.hcos) - np.sqrt(sin_squared) * h.hcos

        # cosines of difference between horizon aspect and slope aspect
        cos_aspect = np.cos(h.azimuth - aspect)

        # integral in equation 7b
        intgrnd = cos_slope * sin_squared + \
            sin_slope * cos_aspect * h_mult

        # intgrnd = cos_slope * sin_squared[key] + \
        #     sin_slope * cos_aspect[key] * h_mult[key]

        # This equation will create basically noise, but add the cos_aspect
        # and that seems to be what introduces the error
        # intgrnd = cos_aspect
        # svf = svf + intgrnd

        ind = intgrnd > 0
        svf[ind] = svf[ind] + intgrnd[ind]

        # svf = svf + hcos[key].azimuth

    svf = svf / len(hcos)

    tcf = (1 + cos_slope)/2 - svf

    return svf, tcf


# def trigtbl(sin_slope, aspect, hcos):
#     """


#     Args:
#         slope: sin(slope) with range from 0 to 1
#         aspect: Aspect as radians from south (aspect 0 is toward
#                 the south) with range from -pi to pi, with negative
#                 values to the west and positive values to the east.
#         hcos: cosines of angles to horizon
#     """

#     # cosine of slopes, sin_slope is provided as sin(slope)
#     cos_slope = np.sqrt((1 - sin_slope) * (1 + sin_slope))

#     # sines and values of horizon angles from zenith
#     sin_squared = {key: None for key in hcos.keys()}
#     h_mult = {key: None for key in hcos.keys()}
#     cos_aspect = {key: None for key in hcos.keys()}
#     for key, h in hcos.items():
#         # sin squared of horizon sin2H
#         sin_squared[key] = (1 - h.hcos) * (1 + h.hcos)

#         # H - sin(H)cos(H)
#         h_mult[key] = np.arccos(h.hcos) - np.sqrt(sin_squared[key]) * h.hcos

#         # cosines of difference between horizon aspect and slope aspect
#         cos_aspect[key] = np.cos(h.azimuth - aspect)
#         # cos_aspect[key] = np.cos(aspect)

#     return cos_slope, sin_squared, h_mult, cos_aspect
