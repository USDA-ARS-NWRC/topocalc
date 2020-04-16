import unittest

import numpy as np

from topocalc.horizon import hor2d_c, horizon


class TestHorizon(unittest.TestCase):

    def test_horizon_dem_errors(self):
        """Test the horizon function errors
        """

        dem = np.ones((10))

        with self.assertRaises(ValueError) as context:
            horizon(0, dem, 1)

        self.assertTrue("horizon input of dem is not a 2D array"
                        in str(context.exception))

    def test_horizon_azimuth_errors(self):
        """Test the horizon function errors
        """

        dem = np.ones((10, 1))

        with self.assertRaises(ValueError) as context:
            horizon(-200, dem, 1)

        self.assertTrue("azimuth must be between -180 and 180 degrees"
                        in str(context.exception))

    def test_hor2dc_errors(self):
        """Test the hor2dc function errors
        """

        dem = np.ones((10))

        with self.assertRaises(ValueError) as context:
            hor2d_c(dem, 1)

        self.assertTrue("hor1d input of z is not a 2D array"
                        in str(context.exception))

    def test_hor2dc_type_errors(self):
        """Test the hor2dc function errors
        """

        dem = np.float32(np.ones((10, 1)))

        with self.assertRaises(ValueError) as context:
            hor2d_c(dem, 1)

        self.assertTrue("hor1d input of z must be a double"
                        in str(context.exception))
