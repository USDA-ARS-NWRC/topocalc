import numpy as np

from topocalc.gradient import gradient_d8
from topocalc.horizon import horizon

def viewf(dem, spacing, nangles=72, method='dozier_2022', sin_slope=None, aspect=None):
    """
    Calculate the sky view factor of a dem, as written in Dozier,2022,

    Dozier, J. (2022). Revisiting topographic horizons in the era of big data and parallel Computing. 
    IEEE Geoscience and Remote Sensing Letters, 19, 1-5.


    Alternatively, it can be ran using equation 7b from Dozier and Frew 1990


    terrain configuration factor (tvf) is defined as:
        (1 + cos(slope))/2 - sky view factor


    Args:
        dem: numpy array for the DEM
        spacing: grid spacing of the DEM
        nangles: number of angles to estimate the horizon, defaults
                to 72 angles
        method: Either 'dozier_2022' or 'dozier_and_frew_1990'
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
        cos_slope = np.cos(slope)
        tan_slope = np.tan(slope)

    # -180 is North
    angles = np.linspace(-180, 180, num=nangles, endpoint=False)

    # Create zeros like array similar to DEM
    svf = np.zeros_like(sin_slope)

    # perform the integral
    # If 1990 is in the method, use Dozier Frew 1990 method.
    if '90' in method:
        for angle in angles:

            # horizon angles
            hcos = horizon(angle, dem, spacing)
            azimuth = np.radians(angle)

            # sin^2(H)
            sin_squared = (1 - hcos) * (1 + hcos)

            # H - sin(H)cos(H)
            h_mult = np.arccos(hcos) - np.sqrt(sin_squared) * hcos

            # cosines of difference between horizon aspect and slope aspect
            cos_aspect = np.cos(azimuth - aspect)

            # integral in equation 7b
            intgrnd = cos_slope * sin_squared + sin_slope * cos_aspect * h_mult

            ind = intgrnd > 0
            svf[ind] = svf[ind] + intgrnd[ind]


    else: # use the updated 2022 method (Default)
        for angle in angles:

            # horizon angles
            hcos = horizon(angle, dem, spacing)
            azimuth = np.radians(angle)

            # H
            h = np.arccos(hcos)

            # cosines of difference between Slope aspect and horizon azimuth
            cos_aspect = np.cos(aspect - azimuth)

            # check for slope being obscured
            # EQ 3 in Dozier et al. 2022
            #     H(t) = min(H(t), acos(sqrt(1-1./(1+tand(slopeDegrees)^2*cos(azmRadian(t)-aspectRadian).^2))));
            t = cos_aspect<0
            h[t] = np.fmin(h[t],np.arccos(np.sqrt(1 - 1/(1 + cos_aspect[t]**2 * tan_slope[t]**2))))

            # integral in Dozier 2022
            # qIntegrand = (cosd(slopeDegrees)*sin(H).^2 + sind(slopeDegrees)*cos(aspectRadian-azmRadian).*(H-cos(H).*sin(H)))/2
            intgrnd = (cos_slope * np.sin(h)**2 + sin_slope*cos_aspect * (h - np.sin(h)*np.cos(h)))

            ind = intgrnd > 0
            svf[ind] = svf[ind] + intgrnd[ind]
    

    # Compute final arrays
    svf = svf / len(angles)
    tcf = (1 + cos_slope)/2 - svf

    return svf, tcf