import numpy as np

from viewf.core_c import topo_core
from viewf.skew import skew, adjust_spacing


def skew_transpose(dem, spacing, angle):
    """Skew and transpose the dem for the given angle.
    Also calculate the new spacing given the skew.

    Arguments:
        dem {array} -- numpy array of dem elevations
        spacing {float} -- grid spacing
        angle {float} -- skew angle

    Returns:
        t -- skew and transpose array
        spacing -- new spacing adjusted for angle
    """

    spacing = adjust_spacing(spacing, np.abs(angle))
    t = skew(dem, angle, fill_min=True).transpose()

    return t, spacing


def horizon(azimuth, dem, spacing):
    """Horizon in one

    TODO expand this description

    Arguments:
        azimuth {float} -- find horizon's along this direction
        dem {np.array2d} -- numpy array of dem elevations
        spacing {float} -- grid spacing

    Returns:
        hcos {np.array} -- cosines of angles to the horizon
    """

    if dem.ndim != 2:
        raise ValueError('viewf input of dem is not a 2D array')

    if azimuth > 180 or azimuth < -180:
        raise ValueError('azimuth must be between -180 and 180 degrees')

    if azimuth == 90:
        # East
        hcos = hor2d_c(dem, spacing, fwd=True)

    elif azimuth == -90:
        # West
        hcos = hor2d_c(dem, spacing, fwd=False)

    elif azimuth == 0:
        # South
        hcos = hor2d_c(dem.transpose(), spacing, fwd=True)
        hcos = hcos.transpose()

    elif np.abs(azimuth) == 180:
        # South
        hcos = hor2d_c(dem.transpose(), spacing, fwd=False)
        hcos = hcos.transpose()

    elif azimuth >= -45 and azimuth <= 45:
        t, spacing = skew_transpose(dem, spacing, azimuth)
        h = hor2d_c(t, spacing, fwd=True)
        hcos = skew(h.transpose(), azimuth, fwd=False)

    elif azimuth <= -135 and azimuth > -180:
        # North west
        a = azimuth + 180
        t, spacing = skew_transpose(dem, spacing, a)
        h = hor2d_c(t, spacing, fwd=False)
        hcos = skew(h.transpose(), a, fwd=False)

    return hcos


def hor2d_c(z, spacing, fwd=True):
    """
    Calculate values of cosines of angles to horizons in 2 dimension, 
    measured from zenith, from elevation difference and distance.  Let
    G be the horizon angle from horizontal and note that:

        sin G = z / sqrt( z^2 + dis^2);

    This result is the same as cos H, where H measured from zenith.

    Args:
        z: elevation array
        spacing: spacing of array

    Returns:
        hcos: cosines of angles to horizon
    """

    if z.ndim != 2:
        raise ValueError('hor1d input of z is not a 2D array')

    if z.dtype != np.double:
        raise ValueError('hor1d input of z must be a double')

    spacing = np.double(spacing)

    # if not fwd:
    #     z = np.ascontiguousarray(np.fliplr(z))
    # else:
    z = np.ascontiguousarray(z)

    h = np.zeros_like(z)
    topo_core.c_hor2d(z, spacing, fwd, h)

    # if not fwd:
    #     h = np.fliplr(h)

    return h
