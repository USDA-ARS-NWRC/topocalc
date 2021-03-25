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


class TestHorizonGold(unittest.TestCase):

    DX = 30

    def calc_gold_horizon(self, surface, gold_index):

        distance = self.DX * np.arange(len(surface))
        hgt = surface[gold_index] - surface
        d = distance[gold_index] - distance

        hcos = hgt / np.sqrt(hgt**2 + d**2)
        hcos[np.isnan(hcos)] = 0

        return hcos

    def assert_horizon(self, surf, gold_index):
        # calculate the gold horizon
        hcos_gold = self.calc_gold_horizon(surf, gold_index)

        # calculate the horizon
        hcos = horizon(90, surf.reshape(1, -1), self.DX)

        np.testing.assert_array_almost_equal(
            hcos_gold.reshape(1, -1),
            hcos,
            decimal=6
        )

    def test_horizon1(self):

        surf = np.array([100.0, 80, 75, 85, 70, 50, 64, 65, 85, 90])
        gold_index = np.array([0, 3, 3, 9, 9, 6, 8, 8, 9, 9])

        self.assert_horizon(surf, gold_index)

    def test_horizon2(self):

        surf = np.array([100.0, 80, 75, 85, 70, 80, 64, 65, 70, 90])
        gold_index = np.array([0, 3, 3, 9, 5, 9, 9, 9, 9, 9])

        self.assert_horizon(surf, gold_index)

    def test_horizon3(self):

        surf = np.array([0.0, 5, 7, 20, 18, 30, 30, 35, 20, 21])
        gold_index = np.array([3, 3, 3, 5, 5, 7, 7, 7, 9, 9])

        self.assert_horizon(surf, gold_index)
