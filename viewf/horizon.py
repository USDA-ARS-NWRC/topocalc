import numpy as np

from viewf.core_c import topo_core


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

    if azimuth == 90:
        hcos = hor2d_c(dem, spacing, fwd=True)

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
