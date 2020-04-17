import numpy as np


def gradient_d4(dem, dx, dy, aspect_rad=False):
    """Calculate the slope and aspect for provided dem,
    this will mimic the original IPW gradient method that
    does a finite difference in the x/y direction.

    Given a center cell e and it's neighbors:

    | a | b | c |
    | d | e | f |
    | g | h | i |

    The rate of change in the x direction is

    [dz/dx] = (f - d ) / (2 * dx)

    The rate of change in the y direction is

    [dz/dy] = (h - b ) / (2 * dy)

    The slope is calculated as

    slope_radians = arctan ( sqrt ([dz/dx]^2 + [dz/dy]^2) )

    Args:
        dem: array of elevation values
        dx: cell size along the x axis
        dy: cell size along the y axis
        aspect_rad: turn the aspect from degrees to IPW radians

    Returns:
        slope in radians
        aspect in degrees or IPW radians
    """

    # Pad the dem
    dem_pad = np.pad(dem, pad_width=1, mode='edge')

    # top
    dem_pad[0, :] = dem_pad[1, :] + (dem_pad[1, :] - dem_pad[2, :])

    # bottom
    dem_pad[-1, :] = dem_pad[-2, :] + (dem_pad[-2, :] - dem_pad[-3, :])

    # left
    dem_pad[:, 0] = dem_pad[:, 1] + (dem_pad[:, 1] - dem_pad[:, 2])

    # right
    dem_pad[:, -1] = dem_pad[:, -2] - (dem_pad[:, -3] - dem_pad[:, -2])

    # finite difference in the y direction
    dz_dy = (dem_pad[2:, 1:-1] - dem_pad[:-2, 1:-1]) / (2 * dy)

    # finite difference in the x direction
    dz_dx = (dem_pad[1:-1, 2:] - dem_pad[1:-1, :-2]) / (2 * dx)

    slope = calc_slope(dz_dx, dz_dy)
    a = aspect(dz_dx, dz_dy)

    if aspect_rad:
        a = aspect_to_ipw_radians(a)

    return slope, a


def gradient_d8(dem, dx, dy, aspect_rad=False):
    """
    Calculate the slope and aspect for provided dem,
    using a 3x3 cell around the center

    Given a center cell e and it's neighbors:

    | a | b | c |
    | d | e | f |
    | g | h | i |

    The rate of change in the x direction is

    [dz/dx] = ((c + 2f + i) - (a + 2d + g) / (8 * dx)

    The rate of change in the y direction is

    [dz/dy] = ((g + 2h + i) - (a + 2b + c)) / (8 * dy)

    The slope is calculated

    slope_radians = arctan ( sqrt ([dz/dx]^2 + [dz/dy]^2) )

    Args:
        dem: array of elevation values
        dx: cell size along the x axis
        dy: cell size along the y axis
        aspect_rad: turn the aspect from degrees to IPW radians

    Returns:
        slope in radians
        aspect in degrees or IPW radians
    """

    # Pad the dem
    dem_pad = np.pad(dem, pad_width=1, mode='edge')

    # top
    dem_pad[0, :] = dem_pad[1, :] + (dem_pad[1, :] - dem_pad[2, :])

    # bottom
    dem_pad[-1, :] = dem_pad[-2, :] + (dem_pad[-2, :] - dem_pad[-3, :])

    # left
    dem_pad[:, 0] = dem_pad[:, 1] + (dem_pad[:, 1] - dem_pad[:, 2])

    # right
    dem_pad[:, -1] = dem_pad[:, -2] - (dem_pad[:, -3] - dem_pad[:, -2])

    # finite difference in the y direction
    dz_dy = ((dem_pad[2:, :-2] + 2*dem_pad[2:, 1:-1] + dem_pad[2:, 2:]) -
             (dem_pad[:-2, :-2] + 2*dem_pad[:-2, 1:-1] +
              dem_pad[:-2, 2:])) / (8 * dy)

    # finite difference in the x direction
    dz_dx = ((dem_pad[:-2, 2:] + 2*dem_pad[1:-1, 2:] + dem_pad[2:, 2:]) -
             (dem_pad[:-2, :-2] + 2*dem_pad[1:-1, :-2] +
              dem_pad[2:, :-2])) / (8 * dx)

    slope = calc_slope(dz_dx, dz_dy)
    a = aspect(dz_dx, dz_dy)

    if aspect_rad:
        a = aspect_to_ipw_radians(a)

    return slope, a


def calc_slope(dz_dx, dz_dy):
    """Calculate the slope given the finite differences

    Arguments:
        dz_dx: finite difference in the x direction
        dz_dy: finite difference in the y direction

    Returns:
        slope numpy array
    """

    return np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))


def aspect(dz_dx, dz_dy):
    """
    Calculate the aspect from the finite difference.
    Aspect is degrees clockwise from North (0/360 degrees)

    See below for a referance to how ArcGIS calculates slope
    http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#/How_Aspect_works/00q900000023000000/

    Args:
        dz_dx: finite difference in the x direction
        dz_dy: finite difference in the y direction

    Returns
        aspect in degrees clockwise from North
    """

    # return in degrees
    a = 180 * np.arctan2(dz_dy, -dz_dx) / np.pi

    aout = 90 - a
    aout[a < 0] = 90 - a[a < 0]
    aout[a > 90] = 360 - a[a > 90] + 90

    # if dz_dy and dz_dx are zero, then handle the
    # special case. Follow the IPW convetion and set
    # the aspect to south or 180 degrees
    idx = (dz_dy == 0) & (dz_dx == 0)
    aout[idx] = 180

    return aout


def aspect_to_ipw_radians(a):
    """
    IPW defines aspect differently than most GIS programs
    so convert an aspect in degrees from due North (0/360)
    to the IPW definition.

    Aspect is radians from south (aspect 0 is toward
    the south) with range from -pi to pi, with negative
    values to the west and positive values to the east

    Args:
        a: aspect in degrees from due North

    Returns
        a: aspect in radians from due South
    """

    arad = np.pi - a * np.pi / 180

    return arad
