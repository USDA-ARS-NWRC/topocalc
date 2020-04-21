import os
import unittest

import numpy as np
from spatialnc import ipw

from topocalc.horizon import horizon


class TestHorizonIPW(unittest.TestCase):
    """
    The test for horizon is slightly different than standard unittests.
    This is because we're comparing the IPW version of horizon to the
    python version. The main difficulty is the bit resolution of the IPW
    images takes the double resolution values, converts them to an integer
    for storage then converts them back to floats. The tests have tried
    to mimic this behaviour and most of the horizon values are extremely
    close.

    Because of the differences in bit resolution and potential differences
    caused by operating systems, the tests are testing that the values
    are close since they are not expected to be equal. There are values
    that are larger than the tollerance but should be less than 6 pixels
    for the 26,208 pixels in the test domain.

    Therefore the tests check that the new python horizon values are close
    and that any large difference are still small.
    """

    @classmethod
    def setUpClass(cls):

        test_dir = os.path.dirname(os.path.abspath(__file__))

        # input DEM
        infile = os.path.join(
            test_dir, 'Lakes/gold_ipw/gold_dem.ipw')
        d = ipw.IPW(infile)

        # C code for hor1d is expecting double
        # the LQ headers have added some small values in the
        # linearization of the image
        cls.gold_dem = np.double(d.bands[0].data)
        cls.spacing = d.bands[0].dline

        # Horizon gold files
        cls.gold_file = os.path.join(
            test_dir, 'Lakes/gold_ipw/horizon/horizon_{}.ipw')

        # to make a fair comparison, first convert the hcos to
        # integers then back using the 16 bit LQ
        # with horizon the float min/max are constant from 0-1
        cls.float_min = 1.0
        cls.float_max = 0.0
        cls.int_min = 0
        cls.int_max = 2**16-1

    def int_to_float(self, x):
        return (self.float_max - self.float_min) * \
            (x / self.int_max) + self.float_min

    def run_horizon(self, azimuth):
        """Run the horizon function for a given azimuth and
        compare with the gold file

        Arguments:
            azimuth {float} -- azimuth to test
        """

        hcos = horizon(azimuth, self.gold_dem, self.spacing)

        # convert the numpy array from a float, to int and back
        h_int = ipw.map_fn(hcos, self.float_min,
                           self.float_max, self.int_min, self.int_max)
        h_float = self.int_to_float(h_int)

        gold = ipw.IPW(self.gold_file.format(azimuth))
        gold_data = gold.bands[0].data

        return gold_data, h_float

    def test_horizon_cardinal(self):
        """Test horizon for cardinal directions"""

        # cardinal directions have much less erro
        for angle in [-180, -90, 0, 90, 180]:
            print('horizon anlge {}'.format(angle))
            gold_data, h_float = self.run_horizon(angle)

            np.testing.assert_allclose(
                h_float, gold_data, rtol=1e-7, atol=1e-4)

    def test_horizon(self):
        """Test horizon for all degrees"""

        atol = 1e-4

        for angle in range(-180, 180, 5):

            gold_data, h_float = self.run_horizon(angle)

            d = gold_data - h_float
            ind = np.abs(d) > atol
            sum_ind = np.sum(ind)
            print('horizon anlge {}: {} value larger than {}, {}'.format(
                angle, sum_ind, atol, d[ind]))

            # This is about 3 degrees
            self.assertTrue(np.all(np.abs(d[ind]) < 0.15))

            # assert that there aren't that many values
            if angle == 70:
                self.assertTrue(sum_ind <= 12)
            else:
                self.assertTrue(sum_ind <= 6)

            h_float[ind] = np.nan
            gold_data[ind] = np.nan

            np.testing.assert_allclose(
                h_float, gold_data, rtol=1e-7, atol=atol)
