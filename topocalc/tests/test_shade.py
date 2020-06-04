import unittest

import numpy as np

from topocalc.gradient import gradient_d8
from topocalc.shade import shade


class TestShade(unittest.TestCase):

    # with self.dx and self.dy equal to 1, the cardinal direction
    # slope values will be np.pi/4 as one of the differences
    # will be zero
    dx = 1
    dy = 1

    dem = np.tile(range(10), (10, 1))

    def calc_slope(self, dem):
        """Calculate the slope

        Arguments:
            dem {numpy} -- dem array
        """

        return gradient_d8(dem, self.dx, self.dy, aspect_rad=True)

    def test_shade_cosz_bounds_error(self):

        with self.assertRaises(Exception) as context:
            shade(0, 0, 0, cosz=1.5)

        self.assertTrue('cosz must be > 0 and <= 1' in str(context.exception))

    def test_shade_zenith_bounds_error(self):

        with self.assertRaises(Exception) as context:
            shade(0, 0, 0, zenith=-10)

        self.assertTrue(
            'Zenith must be >= 0 and < 90' in str(context.exception))

    def test_shade_zenith_cosz_not_specified_error(self):

        with self.assertRaises(Exception) as context:
            shade(0, 0, 0)

        self.assertTrue(
            'Must specify either cosz or zenith' in str(context.exception))

    def test_shade_aspect_degrees_error(self):

        with self.assertRaises(Exception) as context:
            shade(0, 100, 0, zenith=10)

        self.assertTrue(
            'Aspect is not in radians from south' in str(context.exception))

    def test_shade_azimuth_value_error(self):

        with self.assertRaises(Exception) as context:
            shade(0, 0, 360, zenith=10)

        self.assertTrue(
            'Azimuth must be between -180 and 180 degrees' in str(context.exception))  # noqa

    def test_shade_west(self):

        # test west slope and aspect
        dem = np.tile(range(10), (10, 1))
        slope, asp = self.calc_slope(dem)

        zenith = 45
        mu = shade(slope, asp, 0, zenith=zenith)
        mu_cos = shade(slope, asp, 0, cosz=np.cos(zenith * np.pi / 180))

        self.assertAlmostEqual(np.mean(mu), 0.43769265754174774, places=7)
        np.testing.assert_allclose(mu, mu_cos)

    def test_shade_north(self):

        # test north slope and aspect
        dem = np.tile(range(10), (10, 1)).transpose()
        slope, asp = self.calc_slope(dem)

        zenith = 45
        mu = shade(slope, asp, 0, zenith=zenith)
        mu_cos = shade(slope, asp, 0, cosz=np.cos(zenith * np.pi / 180))

        self.assertAlmostEqual(np.mean(mu), 0.0, places=7)
        np.testing.assert_allclose(mu, mu_cos)

    def test_shade_east(self):

        # test east slope and aspect
        dem = np.fliplr(np.tile(range(10), (10, 1)))
        slope, asp = self.calc_slope(dem)

        zenith = 45
        mu = shade(slope, asp, 0, zenith=zenith)
        mu_cos = shade(slope, asp, 0, cosz=np.cos(zenith * np.pi / 180))

        self.assertAlmostEqual(np.mean(mu), 0.43769265754174774, places=7)
        np.testing.assert_allclose(mu, mu_cos)

    def test_shade_south(self):

        # test south slope and aspect
        dem = np.flipud(np.tile(range(10), (10, 1)).transpose())
        slope, asp = self.calc_slope(dem)

        zenith = 45
        mu = shade(slope, asp, 0, zenith=zenith)
        mu_cos = shade(slope, asp, 0, cosz=np.cos(zenith * np.pi / 180))

        self.assertAlmostEqual(np.mean(mu), 0.9930530248115434, places=7)
        np.testing.assert_allclose(mu, mu_cos)
