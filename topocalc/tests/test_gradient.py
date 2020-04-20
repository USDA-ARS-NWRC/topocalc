import unittest

import numpy as np

from topocalc import gradient


class TestGradient(unittest.TestCase):

    # with self.dx and self.dy equal to 1, the cardinal direction
    # slope values will be np.pi/4 as one of the differences
    # will be zero
    dx = 1
    dy = 1

    # with self.dx and self.dy equal to 1, the slope of the 45 degree
    # areas will be arctan(sqrt(2))
    slope_val = np.arctan(np.sqrt(2))

    def gen_dem_nw(self, dem_size=10):
        dem = np.tile(range(10), (10, 1)).transpose()

        for i in range(dem_size):
            dem[i, :] = np.arange(i, i+dem_size)
        return dem

    def gen_dem_sw(self, dem_size=10):
        dem = np.tile(range(10), (10, 1)).transpose()

        for i in range(1, 1+dem_size):
            dem[-i, :] = np.arange(i, i+dem_size)
        return dem

    def gen_dem_se(self, dem_size=10):
        dem = np.tile(range(10), (10, 1)).transpose()

        for i in range(1, 1+dem_size):
            dem[-i, :] = np.arange(i+dem_size, i, -1)
        return dem

    def gen_dem_ne(self, dem_size=10):
        dem = np.tile(range(10), (10, 1)).transpose()

        for i in range(dem_size):
            dem[i, :] = np.arange(i+dem_size, i, -1)
        return dem


class TestGradientD4(TestGradient):

    def test_gradient_d4_west(self):
        """ Test for the gradient_d4 for west """

        # test west slope and aspect
        dem = np.tile(range(10), (10, 1))
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 270))
        self.assertTrue(np.all(ipw_a == -np.pi/2))

    def test_gradient_d4_north(self):
        """ Test for the gradient_d4 for north """

        # test north slope and aspect
        dem = np.tile(range(10), (10, 1)).transpose()
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 0))
        self.assertTrue(np.all(np.abs(ipw_a) == np.pi))

    def test_gradient_d4_east(self):
        """ Test for the gradient_d4 for east """

        # test east slope and aspect
        dem = np.fliplr(np.tile(range(10), (10, 1)))
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 90))
        self.assertTrue(np.all(ipw_a == np.pi/2))

    def test_gradient_d4_south(self):
        """ Test for the gradient_d4 for south """

        # test south slope and aspect
        dem = np.flipud(np.tile(range(10), (10, 1)).transpose())
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 180))
        self.assertTrue(np.all(ipw_a == 0))

    def test_gradient_d4_nw(self):
        """ Test for the gradient_d4 for nw """

        # test northwest slope and aspect
        dem = self.gen_dem_nw()
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 315))
        self.assertTrue(np.all(ipw_a == (-np.pi/2 - np.pi/4)))

    def test_gradient_d4_sw(self):
        """ Test for the gradient_d4 for north """

        # test southwest slope and aspect
        dem = self.gen_dem_sw()
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 225))
        self.assertTrue(np.all(ipw_a == -np.pi/4))

    def test_gradient_d4_se(self):
        """ Test for the gradient_d4 for se """

        # test southeast slope and aspect
        dem = self.gen_dem_se()
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 135))
        self.assertTrue(np.all(ipw_a == np.pi/4))

    def test_gradient_d4_ne(self):
        """ Test for the gradient_d4 for ne """

        # test northeast slope and aspect
        dem = self.gen_dem_ne()
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 45))
        self.assertTrue(np.all(ipw_a == (np.pi/2 + np.pi/4)))

    def test_gradient_d4_flat(self):
        """ Test for the gradient_d4 for flat """

        # test south slope and aspect
        dem = np.ones((10, 10))
        py_slope, asp = gradient.gradient_d4(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == 0))
        self.assertTrue(np.all(asp == 180))
        self.assertTrue(np.all(ipw_a == 0))


class TestGradientD8(TestGradient):

    def test_gradient_d8_west(self):
        """ Test for the gradient_d8 for west """

        # test west slope and aspect
        dem = np.tile(range(10), (10, 1))
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 270))
        self.assertTrue(np.all(ipw_a == -np.pi/2))

    def test_gradient_d8_north(self):
        """ Test for the gradient_d8 for north """

        # test north slope and aspect
        dem = np.tile(range(10), (10, 1)).transpose()
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 0))
        self.assertTrue(np.all(np.abs(ipw_a) == np.pi))

    def test_gradient_d8_east(self):
        """ Test for the gradient_d8 for east """

        # test east slope and aspect
        dem = np.fliplr(np.tile(range(10), (10, 1)))
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 90))
        self.assertTrue(np.all(ipw_a == np.pi/2))

    def test_gradient_d8_south(self):
        """ Test for the gradient_d8 for south """

        # test south slope and aspect
        dem = np.flipud(np.tile(range(10), (10, 1)).transpose())
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == np.pi/4))
        self.assertTrue(np.all(asp == 180))
        self.assertTrue(np.all(ipw_a == 0))

    def test_gradient_d8_nw(self):
        """ Test for the gradient_d8 for nw """

        # test northwest slope and aspect
        dem = self.gen_dem_nw()
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 315))
        self.assertTrue(np.all(ipw_a == (-np.pi/2 - np.pi/4)))

    def test_gradient_d8_sw(self):
        """ Test for the gradient_d8 for sw """

        # test southwest slope and aspect
        dem = self.gen_dem_sw()
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 225))
        self.assertTrue(np.all(ipw_a == -np.pi/4))

    def test_gradient_d8_se(self):
        """ Test for the gradient_d8 for se """

        # test southeast slope and aspect
        dem = self.gen_dem_se()
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 135))
        self.assertTrue(np.all(ipw_a == np.pi/4))

    def test_gradient_d8_ne(self):
        """ Test for the gradient_d8 for ne """

        # test northeast slope and aspect
        dem = self.gen_dem_ne()
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == self.slope_val))
        self.assertTrue(np.all(asp == 45))
        self.assertTrue(np.all(ipw_a == (np.pi/2 + np.pi/4)))

    def test_gradient_d8_flat(self):
        """ Test for the gradient_d8 for flat """

        # test south slope and aspect
        dem = np.ones((10, 10))
        py_slope, asp = gradient.gradient_d8(dem, self.dx, self.dy)
        ipw_a = gradient.aspect_to_ipw_radians(asp)

        self.assertTrue(np.all(py_slope == 0))
        self.assertTrue(np.all(asp == 180))
        self.assertTrue(np.all(ipw_a == 0))
