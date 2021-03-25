import numpy as np

from topocalc.core_c import topo_core
from topocalc.skew import adjust_spacing, skew


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


def transpose_skew(dem, spacing, angle):
    """Transpose, skew then transpose a dem for the
    given angle. Also calculate the new spacing

    Arguments:
        dem {array} -- numpy array of dem elevations
        spacing {float} -- grid spacing
        angle {float} -- skew angle

    Returns:
        t -- skew and transpose array
        spacing -- new spacing adjusted for angle
    """

    t = skew(dem.transpose(), angle, fill_min=True).transpose()
    spacing = adjust_spacing(spacing, np.abs(angle))

    return t, spacing


def horizon(azimuth, dem, spacing):
    """Calculate horizon angles for one direction. Horizon angles
    are based on Dozier and Frew 1990 and are adapted from the
    IPW C code.

    The coordinate system for the azimuth is 0 degrees is South,
    with positive angles through East and negative values
    through West. Azimuth values must be on the -180 -> 0 -> 180
    range.

    Arguments:
        azimuth {float} -- find horizon's along this direction
        dem {np.array2d} -- numpy array of dem elevations
        spacing {float} -- grid spacing

    Returns:
        hcos {np.array} -- cosines of angles to the horizon
    """

    if dem.ndim != 2:
        raise ValueError('horizon input of dem is not a 2D array')

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
        # South west through south east
        t, spacing = skew_transpose(dem, spacing, azimuth)
        h = hor2d_c(t, spacing, fwd=True)
        hcos = skew(h.transpose(), azimuth, fwd=False)

    elif azimuth <= -135 and azimuth > -180:
        # North west
        a = azimuth + 180
        t, spacing = skew_transpose(dem, spacing, a)
        h = hor2d_c(t, spacing, fwd=False)
        hcos = skew(h.transpose(), a, fwd=False)

    elif azimuth >= 135 and azimuth < 180:
        # North East
        a = azimuth - 180
        t, spacing = skew_transpose(dem, spacing, a)
        h = hor2d_c(t, spacing, fwd=False)
        hcos = skew(h.transpose(), a, fwd=False)

    elif azimuth > 45 and azimuth < 135:
        # South east through north east
        a = 90 - azimuth
        t, spacing = transpose_skew(dem, spacing, a)
        h = hor2d_c(t, spacing, fwd=True)
        hcos = skew(h.transpose(), a, fwd=False).transpose()

    elif azimuth < -45 and azimuth > -135:
        # South west through north west
        a = -90 - azimuth
        t, spacing = transpose_skew(dem, spacing, a)
        h = hor2d_c(t, spacing, fwd=False)
        hcos = skew(h.transpose(), a, fwd=False).transpose()

    else:
        ValueError('azimuth not valid')

    # sanity check
    assert hcos.shape == dem.shape

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

    z = np.ascontiguousarray(z)

    h = np.zeros_like(z)
    topo_core.c_hor2d(z, spacing, fwd, h)

    # if not fwd:
    #     h = np.fliplr(h)

    return h


def pyhorizon(dem, dx):
    """Pure python version of the horizon function.

    NOTE: this is fast for small dem's but quite slow
    for larger ones. This is mainly to show that it
    can be done with numpy but requires a bit more to
    remove the for loop over the rows. Also, this just
    calculates the horizon in one direction, need to implement
    the rest of the horizon function for calcuating the
    horizon at an angle.

    Args:
        dem (np.ndarray): dem for the horizon
        dx (float): spacing for the dem

    Returns:
        [tuple]: cosine of the horizon angle and index
            to the horizon.
    """

    # needs to be a float
    if dem.dtype != np.float64:
        dem = dem.astype(np.float64)

    nrows, ncols = dem.shape
    hcos = np.zeros_like(dem)
    horizon_index = np.zeros_like(dem)

    # distance to each point
    # k=-1 because the distance to the point itself is 0
    distance = dx * np.cumsum(np.tri(ncols, ncols, k=-1), axis=0)
    col_index = np.arange(0, ncols)

    for n in range(nrows):
        surface = dem[n, :]

        m = np.repeat(surface.reshape(1, -1), ncols, axis=0)

        # height change
        height = np.tril(m.T - m)

        # slope
        slope = height / distance

        # horizon location
        hor = np.nanargmax(slope[:, :-1], axis=0)
        hor = np.append(hor, ncols-1)
        hidx = hor.astype(int)

        horizon_height_diff = surface[hidx] - surface
        horizon_distance_diff = dx * (hor - col_index)

        new_horizon = horizon_height_diff / \
            np.sqrt(horizon_height_diff**2 + horizon_distance_diff**2)

        new_horizon[new_horizon < 0] = 0
        new_horizon[np.isnan(new_horizon)] = 0

        hcos[n, :] = new_horizon
        horizon_index[n, :] = hidx

    return hcos, horizon_index
