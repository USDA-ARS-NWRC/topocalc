import unittest

import numpy as np
from spatialnc import ipw

from viewf.horizon import horizon


class TestHorizon(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # input DEM
        infile = 'tests/Lakes/gold/gold_dem.ipw'
        d = ipw.IPW(infile)

        # C code for hor1d is expecting double
        # the LQ headers have added some small values in the linearization of the image
        cls.gold_dem = np.double(d.bands[0].data)
        cls.spacing = d.bands[0].dline

        # Horizon gold files
        cls.gold_file = 'tests/Lakes/gold/horizon/horizon_{}.ipw'

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

        np.testing.assert_allclose(h_float, gold_data, rtol=1e-6, atol=1e-4)

    def test_horizon(self):
        """Test horizon for all degrees"""

        for angle in range(-180, 180, 5):
            print('horizon anlge {}'.format(angle))
            self.run_horizon(angle)
