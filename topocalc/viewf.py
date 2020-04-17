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
    Calculate the sky view factor of a dem.

    The sky view factor from equation 7b from Dozier and Frew 1990

    .. math::
        V_d \approx \frac{1}{2\pi} \int_{0}^{2\pi}\left [ cos(S) sin^2{H_\phi} 
        + sin(S)cos(\phi-A) \times \left ( H_\phi - sin(H_\phi) cos(H_\phi)
        \right )\right ] d\phi

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

    """  # noqa

    if dem.ndim != 2:
        raise ValueError('viewf input of dem is not a 2D array')

    if nangles < 16:
        raise ValueError('viewf number of angles should be 16 or greater')

    if sin_slope is not None:
        if np.max(sin_slope) > 1:
            raise ValueError('slope must be sin(slope) with range from 0 to 1')

    # calculate the gradient if not provided
    # The slope is returned as radians so convert to sin(S)
    if sin_slope is None:
        slope, aspect = gradient_d8(
            dem, dx=spacing, dy=spacing, aspect_rad=True)
        sin_slope = np.sin(slope)

    # -180 is North
    angles = np.linspace(-180, 180, num=nangles, endpoint=False)

    # perform the integral
    cos_slope = np.sqrt((1 - sin_slope) * (1 + sin_slope))
    svf = np.zeros_like(sin_slope)
    for angle in angles:

        # horizon angles
        hcos = horizon(angle, dem, spacing)
        azimuth = d2r(angle)

        # sin^2(H)
        sin_squared = (1 - hcos) * (1 + hcos)

        # H - sin(H)cos(H)
        h_mult = np.arccos(hcos) - np.sqrt(sin_squared) * hcos

        # cosines of difference between horizon aspect and slope aspect
        cos_aspect = np.cos(azimuth - aspect)

        # integral in equation 7b
        intgrnd = cos_slope * sin_squared + \
            sin_slope * cos_aspect * h_mult

        ind = intgrnd > 0
        svf[ind] = svf[ind] + intgrnd[ind]

    svf = svf / len(angles)

    tcf = (1 + cos_slope)/2 - svf

    return svf, tcf
