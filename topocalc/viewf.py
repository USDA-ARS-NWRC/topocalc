import numpy as np

from topocalc.gradient import gradient
from topocalc.horizon import horizon


def dozier_2022(angles, dem, spacing, aspect, slope, svf):
    '''
    Sky view factor as calcualted in Dozier,2022

    Dozier, J. (2022). Revisiting topographic horizons in the era of big data and parallel Computing.
    IEEE Geoscience and Remote Sensing Letters, 19, 1-5.

    '''
    # Compute trig
    sin_slope = np.sin(slope)
    cos_slope = np.cos(slope)
    tan_slope = np.tan(slope)

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


def dozier_and_frew_1990(angles, dem, spacing, aspect, slope, svf):
    '''
    Sky view factor as calcualted in Eq 7b Dozier & Frew, 1990:

    .. math::
        V_d \approx \frac{1}{2\pi} \int_{0}^{2\pi}\left [ cos(S) sin^2{H_\phi}
        + sin(S)cos(\phi-A) \times \left ( H_\phi - sin(H_\phi) cos(H_\phi)
        \right )\right ] d\phi


    '''

    # Compute trig
    sin_slope = np.sin(slope)
    cos_slope = np.cos(slope)

    # Loop through n_angles
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

    # Compute final arrays
    svf = svf / len(angles)
    tcf = (1 + cos_slope)/2 - svf

    return svf, tcf



def viewf(dem, spacing, nangles=72, method='dozier_2022', gradient_method="d8"):
    """
    Calculate the sky view factor of a dem, as written in Dozier,2022,

    Dozier, J. (2022). Revisiting topographic horizons in the era of big data and parallel Computing.
    IEEE Geoscience and Remote Sensing Letters, 19, 1-5.

    Alternatively, it can be ran using equation 7b from Dozier and Frew 1990.

    terrain configuration factor (tvf) is defined as:
        (1 + cos(slope))/2 - sky view factor

    Args:
        gradient:
        dem: numpy array for the DEM
        spacing: grid spacing of the DEM
        nangles: number of angles to estimate the horizon, defaults
                to 72 angles
        method: Either 'dozier_2022' or 'dozier_and_frew_1990'
        gradient_method: Method to calculate terrain gradient.
                         Choices: "d4" or "d8" (Default).


    Returns:
        svf: sky view factor
        tcf: terrain configuration factor

    """  # noqa

    if dem.ndim != 2:
        raise ValueError('viewf input of dem is not a 2D array')

    if nangles < 16:
        raise ValueError('viewf number of angles should be 16 or greater')

    slope, aspect = gradient(
        gradient_method, dem, dx=spacing, dy=spacing, aspect_rad=True
    )

    # -180 is North
    angles = np.linspace(-180, 180, num=nangles, endpoint=False)

    # Create zeros like array similar to DEM
    svf = np.zeros_like(dem)

    # perform the integral based on which method
    if method == 'dozier_and_frew_1990':
        svf,tcf = dozier_and_frew_1990(
            angles, dem, spacing, aspect, slope, svf
        )
    elif method == 'dozier_2022':
        svf,tcf = dozier_2022(angles, dem, spacing, aspect, slope, svf)
    else:
        raise Exception("Unknown sky view factor method given")

    return svf, tcf
