import numpy as np


def shade(slope, aspect, azimuth, cosz=None, zenith=None):
    """
    Calculate the cosize of the local illumination angle over a DEM
    Solves the following equation

    cos(ts) = cos(t0) * cos(S) + sin(t0) * sin(S) * cos(phi0 - A)

    where
        t0 is the illumination angle on a horizontal surface
        phi0 is the azimuth of illumination
        S is slope in radians
        A is aspect in radians

    Slope and aspect are expected to come from the IPW gradient command.
    Slope is stored as sin(S) with range from 0 to 1. Aspect is stored
    as radians from south (aspect 0 is toward the south) with range from
    -pi to pi, with negative values to the west and positive values to the
    east.

    Args:
        slope: numpy array of sine of slope angles sin(S)
        aspect: numpy array of aspect in radians from south
        azimuth: azimuth in degrees to the sun -180..180 (comes from sunang)
        cosz: cosize of the zeinith angle 0..1 (comes from sunang)
        zenith: the solar zenith angle 0..90 degrees

    At least one of the cosz or zenith must be specified.  If both are
    specified the zenith is ignored

    Returns:
        mu: numpy matrix of the cosize of the local illumination angle cos(ts)

    The python shade() function is an interpretation of the IPW shade()
    function and follows as close as possible.  All equations are based
    on Dozier & Frew, 1990. 'Rapid calculation of Terrain Parameters For
    Radiation Modeling From Digital Elevation Data,' IEEE TGARS

    """

    # process the options
    if cosz is not None:
        if (cosz <= 0) or (cosz > 1):
            raise Exception('cosz must be > 0 and <= 1')

        ctheta = cosz
        zenith = np.arccos(ctheta)  # in radians
        stheta = np.sin(zenith)

    elif zenith is not None:
        if (zenith < 0) or (zenith >= 90):
            raise Exception('Zenith must be >= 0 and < 90')

        zenith *= np.pi/180.0  # in radians
        ctheta = np.cos(zenith)
        stheta = np.sin(zenith)

    else:
        raise Exception('Must specify either cosz or zenith')

    if np.max(np.abs(aspect)) > np.pi:
        raise Exception('Aspect is not in radians from south')

    if (azimuth > 180) or (azimuth < -180):
        raise Exception('Azimuth must be between -180 and 180 degrees')

    azimuth *= np.pi/180

    # get the cos S from cos^2 + sin^2 = 1
    costbl = np.sqrt((1 - slope) * (1 + slope))

    # cosine of local illumination angle
    mu = ctheta * costbl + stheta * slope * np.cos(azimuth - aspect)

    mu[mu < 0] = 0
    mu[mu > 1] = 1

    return mu
