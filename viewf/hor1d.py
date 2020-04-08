from math import hypot

import numpy as np

from smrf.utils.topo.core import topo_core


def hor1d_c(z, spacing, fwd=True):
    """
    Calculate values of cosines of angles to horizons in 1 dimension, 
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

    if z.ndim != 1:
        raise ValueError('hor1d input of z is not a 1D array')

    h = np.zeros_like(z)
    topo_core.c_hor1d(z, spacing, fwd, h)

    return h


def hor1d(z, spacing, fwd=True):
    """
    Calculate values of cosines of angles to horizons, measured
    from zenith, from elevation difference and distance.  Let
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

    hcos = np.zeros_like(z)
    nrow = z.shape[0]

    for i in range(nrow):
        if fwd:
            h = hor1f(z[i, :])
        else:
            h = hor1b(z[i, :])
        hcos[i, :] = horval(z[i, :], spacing, h)

    return hcos


def horval(z, delta, h):
    """
    Calculate values of cosines of angles to horizons, measured
    from zenith, from elevation difference and distance.  Let
    G be the horizon angle from horizontal and note that:

        sin G = z / sqrt( z^2 + dis^2);

    This result is the same as cos H, where H measured from zenith.

    Args:
        z: elevation vector
        delta: spacing
        h: horizon function output

    Returns:
        hcos: cosines of angles to horizon
    """

    hcos = np.zeros_like(z)
    for i in range(len(z)):

        # grid points to horizon
        j = h[i]
        d = j - i

        # point is its own horizon
        if (d == 0):
            hcos[i] = 0

        # else need to calculate sine */
        else:
            if (d < 0):
                d = -d

            diff = z[j] - z[i]
            hcos[i] = diff / hypot(diff, d * delta)

    return hcos


def hor1f(z):
    """
    Calculate the horizon pixel for all z
    This mimics the algorthim from Dozier 1981 and the
    hor1f.c from IPW

    Works backwards from the end but looks forwards for
    the horizon

    Args:
        z - elevations for the points

    Returns:
        h - index to the horizon point

    20150601 Scott Havens
    20191025 Scott Havens
    """

    N = len(z)  # number of points to look at
    # x = np.array(x)
    z = np.array(z)

    # preallocate the h array to zeros, what ealloc is doing
    h = np.zeros(N, dtype=int)

    # the end point is it's own horizon
    h[N-1] = N-1

    # loop runs from next-to-end backwards to the beginning
    # range end is -1 to get the 0 index
    for i in range(N-2, -1, -1):

        zi = z[i]

        # Start with next-to-adjacent point in either forward or backward
        # direction, depending on which way loop is running. Note that we
        # don't consider the adjacent point; this seems to help reduce noise.
        k = i + 2

        if k >= N:
            k -= 1

        # loop until horizon is found
        j = k
        k = h[j]
        sij = _slopef(i, zi, j, z[j])
        sihj = _slopef(i, zi, k, z[k])

        # if slope(i,j) >= slope(i,h[j]), horizon has been found; otherwise
        # set j to k (=h[j]) and loop again
        # or if we are at the end of the section
        while sij < sihj:

            j = k
            k = h[j]

            sij = _slopef(i, zi, j, z[j])
            sihj = _slopef(i, zi, k, z[k])

        # if slope(i,j) > slope(j,h[j]), j is i's horizon; else if slope(i,j)
        # is zero, i is its own horizon; otherwise slope(i,j) = slope(i,h[j])
        # so h[j] is i's horizon
        if sij > sihj:
            h[i] = j
        elif sij == 0:
            h[i] = i
        else:
            h[i] = k

    return h


def hor1b(z):
    """
    Calculate the horizon pixel for all z
    This mimics the algorthim from Dozier 1981 and the
    hor1b.c from IPW

    Works forward from the start but looks backwards for
    the horizon

    Args:
        z - elevations for the points

    Returns:
        h - index to the horizon point

    """

    N = len(z)  # number of points to look at
    # x = np.array(x)
    z = np.array(z)

    # preallocate the h array to zeros, what ealloc is doing
    h = np.zeros(N, dtype=int)

    # the end point is it's own horizon
    h[0] = 0

    # loop runs from next-to-end backwards to the beginning
    # range end is -1 to get the 0 index
    for i in range(1, N, 1):

        zi = z[i]

        # Start with next-to-adjacent point in either forward or backward
        # direction, depending on which way loop is running. Note that we
        # don't consider the adjacent point; this seems to help reduce noise.
        k = i - 2

        if k < 0:
            k += 1

        # loop until horizon is found
        j = k
        k = h[j]
        sij = _slopeb(i, zi, j, z[j])
        sihj = _slopeb(i, zi, k, z[k])

        # if slope(i,j) >= slope(i,h[j]), horizon has been found; otherwise
        # set j to k (=h[j]) and loop again
        # or if we are at the end of the section
        while sij < sihj:

            j = k
            k = h[j]

            sij = _slopeb(i, zi, j, z[j])
            sihj = _slopeb(i, zi, k, z[k])

        # if slope(i,j) > slope(j,h[j]), j is i's horizon; else if slope(i,j)
        # is zero, i is its own horizon; otherwise slope(i,j) = slope(i,h[j])
        # so h[j] is i's horizon
        if sij > sihj:
            h[i] = j
        elif sij == 0:
            h[i] = i
        else:
            h[i] = k

    return h


def _slopef(xi, zi, xj, zj):
    """
    Slope between the two points only if the pixel is higher
    than the other
    """

    if zj <= zi:
        return 0
    else:
        return (zj - zi) / (xj - xi)


def _slopeb(xi, zi, xj, zj):
    """
    Slope between the two points only if the pixel is higher
    than the other
    """

    if zj <= zi:
        return 0
    else:
        return (zj - zi) / (xi - xj)
